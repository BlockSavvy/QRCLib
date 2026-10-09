import { gcm } from "@noble/ciphers/aes.js";
import { ed25519, x25519 } from "@noble/curves/ed25519.js";
import { secp256k1 } from "@noble/curves/secp256k1.js";
import { hkdf } from "@noble/hashes/hkdf.js";
import { ripemd160 } from "@noble/hashes/legacy.js";
import { sha256 } from "@noble/hashes/sha2.js";
import { sha3_256, shake256 } from "@noble/hashes/sha3.js";
import { ml_dsa65 } from "@noble/post-quantum/ml-dsa.js";
import { ml_kem768 } from "@noble/post-quantum/ml-kem.js";
import { slh_dsa_sha2_128f } from "@noble/post-quantum/slh-dsa.js";

export const XWING_LABEL = Uint8Array.from([0x5c, 0x2e, 0x2f, 0x2f, 0x5e, 0x5c]);
const SIGN_DOMAIN = new TextEncoder().encode("QRCL-HYBRID-SIGN-v1");
const SALT = new TextEncoder().encode("qrclib-v1");

export const SIZES = {
  xwingPk: 1216,
  xwingSk: 32,
  xwingCt: 1120,
  hybridPk: 1984,
  hybridSig: 3373,
  mldsaPk: 1952,
  mldsaSig: 3309,
  edPk: 32,
  edSig: 64,
  mlkemPk: 1184,
  mlkemCt: 1088,
} as const;

export function randomBytes(length: number): Uint8Array {
  const bytes = new Uint8Array(length);
  crypto.getRandomValues(bytes);
  return bytes;
}

export function concat(...parts: Uint8Array[]): Uint8Array {
  const out = new Uint8Array(parts.reduce((n, part) => n + part.length, 0));
  let offset = 0;
  for (const part of parts) {
    out.set(part, offset);
    offset += part.length;
  }
  return out;
}

export function equalBytes(a: Uint8Array, b: Uint8Array): boolean {
  if (a.length !== b.length) return false;
  let diff = 0;
  for (let i = 0; i < a.length; i += 1) diff |= a[i] ^ b[i];
  return diff === 0;
}

export function toHex(bytes: Uint8Array, max?: number): string {
  const slice = max ? bytes.subarray(0, max) : bytes;
  const hex = Array.from(slice, (byte) => byte.toString(16).padStart(2, "0")).join("");
  return max && bytes.length > max ? `${hex}…` : hex;
}

export function utf8(value: string): Uint8Array {
  return new TextEncoder().encode(value);
}

function derive(shared: Uint8Array, info: string): Uint8Array {
  return hkdf(sha256, shared, SALT, utf8(info), 32);
}

export type XwingKeys = { publicKey: Uint8Array; secretKey: Uint8Array };

function expand(secret: Uint8Array) {
  if (secret.length !== 32) throw new Error("X-Wing secret must be 32 bytes");
  const expanded = shake256(secret, { dkLen: 96 });
  const kem = ml_kem768.keygen(expanded.slice(0, 64));
  const scalar = expanded.slice(64, 96);
  const xPublic = x25519.getPublicKey(scalar);
  if (kem.publicKey.length !== SIZES.mlkemPk || xPublic.length !== 32) {
    throw new Error("unexpected X-Wing component size");
  }
  return { kemSecret: kem.secretKey, kemPublic: kem.publicKey, scalar, xPublic };
}

export function xwingFromSeed(seed: Uint8Array): XwingKeys {
  const { kemPublic, xPublic } = expand(seed);
  return { publicKey: concat(kemPublic, xPublic), secretKey: seed.slice() };
}

export function generateXwing(): XwingKeys {
  return xwingFromSeed(randomBytes(32));
}

export function xwingEncapsulate(publicKey: Uint8Array): { ciphertext: Uint8Array; shared: Uint8Array } {
  if (publicKey.length !== SIZES.xwingPk) throw new Error("X-Wing public key must be 1216 bytes");
  const kemPublic = publicKey.subarray(0, SIZES.mlkemPk);
  const xPublic = publicKey.subarray(SIZES.mlkemPk);
  const ephemeral = randomBytes(32);
  const ctX = x25519.getPublicKey(ephemeral);
  const ssX = x25519.getSharedSecret(ephemeral, xPublic);
  if (ssX.length !== 32 || ctX.length !== 32) throw new Error("X25519 size");
  const { cipherText, sharedSecret } = ml_kem768.encapsulate(kemPublic);
  const shared = sha3_256(concat(sharedSecret, ssX, ctX, xPublic, XWING_LABEL));
  return { ciphertext: concat(cipherText, ctX), shared };
}

export function xwingDecapsulate(secretKey: Uint8Array, ciphertext: Uint8Array): Uint8Array {
  if (ciphertext.length !== SIZES.xwingCt) throw new Error("X-Wing ciphertext must be 1120 bytes");
  const { kemSecret, scalar, xPublic } = expand(secretKey);
  const ctM = ciphertext.subarray(0, SIZES.mlkemCt);
  const ctX = ciphertext.subarray(SIZES.mlkemCt);
  const ssM = ml_kem768.decapsulate(ctM, kemSecret);
  const ssX = x25519.getSharedSecret(scalar, ctX);
  return sha3_256(concat(ssM, ssX, ctX, xPublic, XWING_LABEL));
}

export type HybridSignKeys = {
  publicKey: Uint8Array;
  mldsaSecret: Uint8Array;
  edSecret: Uint8Array;
};

export function generateHybridSign(): HybridSignKeys {
  const lattice = ml_dsa65.keygen();
  const classical = ed25519.keygen();
  const edSecret = classical.secretKey.length === 32 ? classical.secretKey : classical.secretKey.subarray(0, 32);
  const edPublic = ed25519.getPublicKey(edSecret);
  return {
    publicKey: concat(lattice.publicKey, edPublic),
    mldsaSecret: lattice.secretKey,
    edSecret,
  };
}

function bind(message: Uint8Array, context: Uint8Array): Uint8Array {
  if (context.length > 255) throw new Error("context must be at most 255 bytes");
  return concat(SIGN_DOMAIN, Uint8Array.of(context.length), context, message);
}

export function hybridSign(keys: HybridSignKeys, message: Uint8Array, context = new Uint8Array()): Uint8Array {
  const payload = bind(message, context);
  return concat(ml_dsa65.sign(payload, keys.mldsaSecret), ed25519.sign(payload, keys.edSecret));
}

export function hybridVerify(
  publicKey: Uint8Array,
  message: Uint8Array,
  signature: Uint8Array,
  context = new Uint8Array(),
): boolean {
  if (publicKey.length !== SIZES.hybridPk || signature.length !== SIZES.hybridSig) return false;
  const payload = bind(message, context);
  const lattice = ml_dsa65.verify(signature.subarray(0, SIZES.mldsaSig), payload, publicKey.subarray(0, SIZES.mldsaPk));
  const classical = ed25519.verify(signature.subarray(SIZES.mldsaSig), payload, publicKey.subarray(SIZES.mldsaPk));
  return lattice && classical;
}

export function sessionKey(shared: Uint8Array): Uint8Array {
  return derive(shared, "qrclib-session-v1");
}

export function encryptMessage(key: Uint8Array, plaintext: Uint8Array): { nonce: Uint8Array; body: Uint8Array } {
  const nonce = randomBytes(12);
  const body = gcm(key, nonce, utf8("qrclib-msg-v1")).encrypt(plaintext);
  return { nonce, body };
}

export function decryptMessage(key: Uint8Array, nonce: Uint8Array, body: Uint8Array): Uint8Array {
  return gcm(key, nonce, utf8("qrclib-msg-v1")).decrypt(body);
}

const B58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz";

function b58encode(data: Uint8Array): string {
  let number = 0n;
  for (const byte of data) number = (number << 8n) + BigInt(byte);
  let chars = "";
  while (number > 0n) {
    const rem = number % 58n;
    number /= 58n;
    chars = B58[Number(rem)] + chars;
  }
  let pad = 0;
  for (const byte of data) {
    if (byte === 0) pad += 1;
    else break;
  }
  return "1".repeat(pad) + chars;
}

export function p2pkh(compressed: Uint8Array): string {
  if (compressed.length !== 33) throw new Error("compressed pubkey");
  const hashed = ripemd160(sha256(compressed));
  const payload = concat(Uint8Array.of(0), hashed);
  const checksum = sha256(sha256(payload)).subarray(0, 4);
  return b58encode(concat(payload, checksum));
}

export type BtcWallet = {
  secretKey: Uint8Array;
  publicKey: Uint8Array;
  address: string;
  signing: HybridSignKeys;
};

export function generateWallet(): BtcWallet {
  const keys = secp256k1.keygen();
  const publicKey = keys.publicKey.length === 33 ? keys.publicKey : secp256k1.getPublicKey(keys.secretKey, true);
  return {
    secretKey: keys.secretKey,
    publicKey,
    address: p2pkh(publicKey),
    signing: generateHybridSign(),
  };
}

export function attest(wallet: BtcWallet, txidHex: string, timestamp: string): {
  signature: Uint8Array;
  commitment: Uint8Array;
  script: Uint8Array;
  message: Uint8Array;
} {
  if (!/^[0-9a-fA-F]{64}$/.test(txidHex)) throw new Error("txid must be 64 hex characters");
  const stamp = utf8(timestamp);
  const tx = Uint8Array.from(txidHex.match(/../g)!.map((byte) => parseInt(byte, 16)));
  const message = concat(
    utf8("QRCL-BTC-ATTEST-v1\n"),
    tx,
    wallet.publicKey,
    wallet.signing.publicKey,
    Uint8Array.of(stamp.length),
    stamp,
  );
  const signature = hybridSign(wallet.signing, message);
  const commitment = sha256(concat(message, signature));
  return { signature, commitment, script: concat(Uint8Array.of(0x6a, 0x20), commitment), message };
}

export type Bench = {
  kemMs: number;
  signMs: number;
  matched: boolean;
  tamperRejected: boolean;
  xwingPk: number;
  xwingCt: number;
  hybridSig: number;
};

export function runBench(): Bench {
  const t0 = performance.now();
  const keys = generateXwing();
  const encapsulated = xwingEncapsulate(keys.publicKey);
  const recovered = xwingDecapsulate(keys.secretKey, encapsulated.ciphertext);
  const kemMs = performance.now() - t0;
  const t1 = performance.now();
  const signing = generateHybridSign();
  const message = utf8("pqcl bench");
  const signature = hybridSign(signing, message);
  const ok = hybridVerify(signing.publicKey, message, signature);
  const flipped = new Uint8Array(signature);
  flipped[flipped.length - 1] ^= 1;
  const tamperRejected = ok && !hybridVerify(signing.publicKey, message, flipped);
  const signMs = performance.now() - t1;
  return {
    kemMs,
    signMs,
    matched: equalBytes(recovered, encapsulated.shared),
    tamperRejected,
    xwingPk: keys.publicKey.length,
    xwingCt: encapsulated.ciphertext.length,
    hybridSig: signature.length,
  };
}

export const SLH_SHA2_128F = { publicKey: 32, secretKey: 64, signature: 17088 } as const;
export const SLH_SHA2_128S_SIGNATURE = 7856;

export function generateSlh(): { publicKey: Uint8Array; secretKey: Uint8Array } {
  return slh_dsa_sha2_128f.keygen();
}

export function slhSign(secretKey: Uint8Array, message: Uint8Array): Uint8Array {
  return slh_dsa_sha2_128f.sign(message, secretKey);
}

export function slhVerify(publicKey: Uint8Array, message: Uint8Array, signature: Uint8Array): boolean {
  if (signature.length !== SLH_SHA2_128F.signature || publicKey.length !== SLH_SHA2_128F.publicKey) return false;
  return slh_dsa_sha2_128f.verify(signature, message, publicKey);
}
