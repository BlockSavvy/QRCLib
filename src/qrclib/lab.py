"""JSON stdin/stdout driver for the browser lab. Not a stable API."""

from __future__ import annotations

import hashlib
import json
import sys
import time

from qrclib.hybrid import generate_kem_keys, generate_sign_keys
from qrclib.lhe import evaluate, open_result, open_values, seal


def _fingerprint(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()[:16]


def run(payload: dict) -> dict:
    values = [float(v) for v in payload["values"]]
    op = payload.get("op", "mean")
    started = time.perf_counter()
    recipient = generate_kem_keys()
    sender = generate_sign_keys()
    envelope = seal(values, recipient.public_key, sender.secret_key)
    # The agent path receives the envelope and the sender public key only.
    result = evaluate(envelope, op, sender.public_key)
    opened = open_values(envelope, recipient.secret_key, sender.public_key)
    homomorphic = open_result(envelope, result, recipient.secret_key, sender.public_key)
    exact = {
        "sum": sum(values),
        "mean": sum(values) / len(values),
    }[op]
    elapsed = time.perf_counter() - started
    return {
        "ok": True,
        "op": op,
        "n": len(values),
        "envelope_bytes": len(envelope),
        "result_bytes": len(result.serialize()),
        "ciphertext_fingerprint": _fingerprint(result.ciphertext),
        "exact": exact,
        "homomorphic": homomorphic,
        "abs_error": abs(homomorphic - exact),
        "opened_values": opened,
        "agent_had_secret": False,
        "milliseconds": round(elapsed * 1000, 1),
    }


def main() -> None:
    try:
        payload = json.loads(sys.stdin.read() or "{}")
        json.dump(run(payload), sys.stdout)
    except Exception as exc:  # noqa: BLE001 — this process is a boundary
        json.dump({"ok": False, "error": f"{type(exc).__name__}: {exc}"}, sys.stdout)
        sys.exit(0)


if __name__ == "__main__":
    main()
