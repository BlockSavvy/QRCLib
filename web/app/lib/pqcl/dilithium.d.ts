export interface KeyPair {
  signingKey: Buffer;
  verificationKey: Buffer;
}

export function generateKeys(): Promise<KeyPair>;
export function sign(message: string, signingKey: Buffer): Promise<Buffer>;
export function verify(message: string, signature: Buffer, verificationKey: Buffer): Promise<boolean>; 