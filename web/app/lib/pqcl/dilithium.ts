import { ml_dsa65 } from "@noble/post-quantum/ml-dsa.js";

/** ML-DSA-65 (FIPS 204). Same algorithm as qrclib.dsa.DEFAULT. */

export interface KeyPair {
  signingKey: Buffer;
  verificationKey: Buffer;
}

export async function generateKeys(): Promise<KeyPair> {
  const keys = ml_dsa65.keygen();
  return {
    signingKey: Buffer.from(keys.secretKey),
    verificationKey: Buffer.from(keys.publicKey),
  };
}

export async function sign(message: string, signingKey: Buffer): Promise<Buffer> {
  const signature = ml_dsa65.sign(new TextEncoder().encode(message), new Uint8Array(signingKey));
  return Buffer.from(signature);
}

export async function verify(
  message: string,
  signature: Buffer,
  verificationKey: Buffer,
): Promise<boolean> {
  try {
    return ml_dsa65.verify(
      new Uint8Array(signature),
      new TextEncoder().encode(message),
      new Uint8Array(verificationKey),
    );
  } catch {
    return false;
  }
}
