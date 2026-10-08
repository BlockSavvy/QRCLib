"""Lattice homomorphic envelope for numeric columns.

The recipient (or a marketplace agent) gets CKKS ciphertexts under a public
SEAL context. Sums, means, shifts, scales, and plaintext masks run without
the secret. The secret context itself is sealed to the recipient with X-Wing
and the whole package is signed with the hybrid signature.

TenSEAL is optional. ``pip install 'qrclib[fhe]'``.

Threat model: the agent is semi-honest. It can return a substituted result
ciphertext; CKKS does not make that substitution detectable. The envelope
signature stops an outsider from widening the policy or swapping the payload
the agent was given. It does not make the agent honest.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass

from qrclib.errors import FHEUnavailable, InvalidSeal, PolicyError
from qrclib.hybrid import HYBRID_SIGN_SIG_LEN, XWING_PK_LEN, sign, verify
from qrclib.kdf import hkdf_sha256
from qrclib.seal import open_seal, seal as hybrid_seal

MAGIC = b"QRLHE1"
RESULT_MAGIC = b"QRLHR1"
_OPS = {"sum": 1, "mean": 2, "shift": 3, "scale": 4, "mask": 5}
_FROM_OP = {code: name for name, code in _OPS.items()}
MAX_VALUES = 16
_POLY = 8192
_MODULI = [50, 30, 50]
_SCALE = 1 << 30


def _tenseal():
    try:
        import tenseal as ts
    except ImportError as exc:
        raise FHEUnavailable(
            "CKKS needs TenSEAL. Install it with: pip install 'qrclib[fhe]'"
        ) from exc
    return ts


def _numbers(values: list[float]) -> list[float]:
    if not 1 <= len(values) <= MAX_VALUES:
        raise ValueError(f"expected 1..{MAX_VALUES} numbers, got {len(values)}")
    cleaned: list[float] = []
    for value in values:
        number = float(value)
        if not math.isfinite(number) or abs(number) > 1_000_000:
            raise ValueError("each value must be finite and within 1e6 of zero")
        cleaned.append(number)
    return cleaned


def _context():
    ts = _tenseal()
    ctx = ts.context(
        ts.SCHEME_TYPE.CKKS,
        poly_modulus_degree=_POLY,
        coeff_mod_bit_sizes=_MODULI,
    )
    ctx.global_scale = _SCALE
    return ts, ctx


@dataclass(frozen=True)
class EvalResult:
    op: str
    ciphertext: bytes
    detail: bytes

    def serialize(self) -> bytes:
        if self.op not in _OPS:
            raise ValueError(f"unknown op {self.op}")
        detail = bytes(self.detail)
        if len(detail) > 65535:
            raise ValueError("detail is too long")
        return (
            RESULT_MAGIC
            + bytes([_OPS[self.op]])
            + len(detail).to_bytes(2, "big")
            + detail
            + len(self.ciphertext).to_bytes(4, "big")
            + self.ciphertext
        )

    @staticmethod
    def parse(data: bytes) -> EvalResult:
        raw = bytes(data)
        if len(raw) < 6 + 1 + 2 + 4 or raw[:6] != RESULT_MAGIC:
            raise InvalidSeal("bad evaluation result")
        op = _FROM_OP.get(raw[6])
        if op is None:
            raise InvalidSeal("unknown evaluation op")
        detail_len = int.from_bytes(raw[7:9], "big")
        start = 9 + detail_len
        if start + 4 > len(raw):
            raise InvalidSeal("truncated evaluation detail")
        detail = raw[9:start]
        ct_len = int.from_bytes(raw[start : start + 4], "big")
        ciphertext = raw[start + 4 :]
        if len(ciphertext) != ct_len:
            raise InvalidSeal("truncated evaluation ciphertext")
        return EvalResult(op, ciphertext, detail)


def seal(
    values: list[float],
    recipient_public: bytes,
    sender_secret: bytes,
    policy: dict | None = None,
) -> bytes:
    """Encrypt ``values`` under CKKS and wrap the secret context for the recipient."""
    numbers = _numbers(values)
    rules = {
        "v": 1,
        "ops": ["sum", "mean", "shift", "scale", "mask"],
        "label": "",
    }
    if policy:
        rules.update(policy)
        unknown = set(rules["ops"]) - set(_OPS)
        if unknown:
            raise ValueError(f"policy lists unknown ops: {sorted(unknown)}")
    ts, ctx = _context()
    secret_blob = ctx.serialize(save_secret_key=True)
    public_ctx = ctx.copy()
    public_ctx.make_context_public()
    public_blob = public_ctx.serialize()
    columns = [ts.ckks_vector(ctx, [number]).serialize() for number in numbers]
    wrapped = hybrid_seal(recipient_public, secret_blob, sender_secret, aad=b"lhe-secret")
    policy_bytes = json.dumps(rules, separators=(",", ":"), sort_keys=True).encode("utf-8")
    if len(policy_bytes) > 65535:
        raise ValueError("policy is too long")
    body = bytearray()
    body += MAGIC
    body += bytes([1])
    body += recipient_public
    body += len(wrapped).to_bytes(4, "big")
    body += wrapped
    body += len(public_blob).to_bytes(4, "big")
    body += public_blob
    body += len(columns).to_bytes(2, "big")
    for column in columns:
        body += len(column).to_bytes(4, "big")
        body += column
    body += len(policy_bytes).to_bytes(2, "big")
    body += policy_bytes
    return bytes(body) + sign(sender_secret, bytes(body))


def _parse(envelope: bytes, sender_public: bytes) -> dict:
    raw = bytes(envelope)
    if len(raw) < len(MAGIC) + 1 + XWING_PK_LEN + HYBRID_SIGN_SIG_LEN:
        raise InvalidSeal("truncated envelope")
    signed, signature = raw[:-HYBRID_SIGN_SIG_LEN], raw[-HYBRID_SIGN_SIG_LEN:]
    if not verify(sender_public, signed, signature):
        raise InvalidSeal("envelope signature rejected")
    if signed[:6] != MAGIC or signed[6] != 1:
        raise InvalidSeal("unsupported envelope")
    offset = 7
    recipient = signed[offset : offset + XWING_PK_LEN]
    offset += XWING_PK_LEN

    def take(n: int) -> bytes:
        nonlocal offset
        chunk = signed[offset : offset + n]
        if len(chunk) != n:
            raise InvalidSeal("truncated envelope field")
        offset += n
        return chunk

    wrap_len = int.from_bytes(take(4), "big")
    wrapped = take(wrap_len)
    pub_len = int.from_bytes(take(4), "big")
    public_blob = take(pub_len)
    count = int.from_bytes(take(2), "big")
    if not 1 <= count <= MAX_VALUES:
        raise InvalidSeal("column count out of range")
    columns = []
    for _ in range(count):
        size = int.from_bytes(take(4), "big")
        columns.append(take(size))
    policy_len = int.from_bytes(take(2), "big")
    policy = json.loads(take(policy_len).decode("utf-8"))
    if offset != len(signed):
        raise InvalidSeal("trailing unsigned bytes")
    return {
        "recipient": recipient,
        "wrapped": wrapped,
        "public": public_blob,
        "columns": columns,
        "policy": policy,
    }


def _allowed(policy: dict, op: str) -> None:
    ops = policy.get("ops", [])
    if op not in ops:
        raise PolicyError(f"{op} is not in the signed policy")


def _reduce(columns: list[bytes], public_blob: bytes, transform):
    ts = _tenseal()
    ctx = ts.context_from(public_blob)
    accumulator = None
    for index, column in enumerate(columns):
        term = transform(ts.ckks_vector_from(ctx, column), index)
        accumulator = term if accumulator is None else accumulator + term
    if accumulator is None:
        raise InvalidSeal("empty column set")
    return accumulator


def evaluate(
    envelope: bytes,
    op: str,
    sender_public: bytes,
    operand: float | list[float] | None = None,
) -> EvalResult:
    """Run one allowed operation. Needs the sender's public key, not the secret."""
    if op not in _OPS:
        raise ValueError(f"unknown op {op}")
    parsed = _parse(envelope, sender_public)
    _allowed(parsed["policy"], op)
    columns: list[bytes] = parsed["columns"]
    count = len(columns)

    if op == "sum":
        vector = _reduce(columns, parsed["public"], lambda term, _i: term)
        detail = b"{}"
    elif op == "mean":
        vector = _reduce(columns, parsed["public"], lambda term, _i: term) * (1.0 / count)
        detail = json.dumps({"n": count}).encode("utf-8")
    elif op == "shift":
        if not isinstance(operand, (int, float)) or isinstance(operand, bool):
            raise ValueError("shift operand must be a number")
        delta = float(operand)
        if not math.isfinite(delta) or abs(delta) > 1_000_000:
            raise ValueError("shift out of range")
        vector = _reduce(columns, parsed["public"], lambda term, _i: term) + [delta]
        detail = json.dumps({"operand": delta}).encode("utf-8")
    elif op == "scale":
        if not isinstance(operand, (int, float)) or isinstance(operand, bool):
            raise ValueError("scale operand must be a number")
        factor = float(operand)
        if not math.isfinite(factor) or abs(factor) > 1_000_000:
            raise ValueError("scale out of range")
        vector = _reduce(columns, parsed["public"], lambda term, _i: term) * factor
        detail = json.dumps({"operand": factor}).encode("utf-8")
    else:
        if not isinstance(operand, (list, tuple)) or len(operand) != count:
            raise ValueError("mask must be a list with one weight per value")
        weights = []
        for weight in operand:
            number = float(weight)
            if not math.isfinite(number) or abs(number) > 1_000_000:
                raise ValueError("mask weight out of range")
            weights.append(number)

        def apply(term, index: int):
            return term * weights[index]

        vector = _reduce(columns, parsed["public"], apply)
        detail = json.dumps({"mask": weights}).encode("utf-8")

    return EvalResult(op, vector.serialize(), detail)


def _secret_context(envelope: bytes, recipient_secret: bytes, sender_public: bytes):
    parsed = _parse(envelope, sender_public)
    secret_blob = open_seal(
        recipient_secret,
        parsed["wrapped"],
        sender_public,
        aad=b"lhe-secret",
    )
    ts = _tenseal()
    return ts, parsed, ts.context_from(secret_blob)


def open_values(envelope: bytes, recipient_secret: bytes, sender_public: bytes) -> list[float]:
    ts, parsed, ctx = _secret_context(envelope, recipient_secret, sender_public)
    opened = []
    for column in parsed["columns"]:
        opened.append(float(ts.ckks_vector_from(ctx, column).decrypt()[0]))
    return opened


def open_result(
    envelope: bytes,
    result: EvalResult | bytes,
    recipient_secret: bytes,
    sender_public: bytes,
) -> float:
    if isinstance(result, (bytes, bytearray)):
        result = EvalResult.parse(result)
    _secret_ctx = _secret_context(envelope, recipient_secret, sender_public)
    ts, _parsed, ctx = _secret_ctx
    return float(ts.ckks_vector_from(ctx, result.ciphertext).decrypt()[0])


def result_from_bytes(data: bytes) -> EvalResult:
    return EvalResult.parse(data)
