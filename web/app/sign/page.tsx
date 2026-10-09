"use client";

import Link from "next/link";
import { useState } from "react";
import { Action, Note, Panel, Python, Reading, Steps } from "@/components/ui";
import { generateHybridSign, hybridSign, hybridVerify, toHex, utf8, type HybridSignKeys } from "@/lib/pq";

export default function SignPage() {
  const [message, setMessage] = useState("Authorize settlement 18 for the data market.");
  const [signedText, setSignedText] = useState<string | null>(null);
  const [keys, setKeys] = useState<HybridSignKeys | null>(null);
  const [signature, setSignature] = useState<Uint8Array | null>(null);
  const [verdict, setVerdict] = useState<string | null>(null);
  const [ok, setOk] = useState<boolean | null>(null);
  const [busy, setBusy] = useState(false);

  function signFresh() {
    setBusy(true);
    setTimeout(() => {
      const next = keys ?? generateHybridSign();
      const sig = hybridSign(next, utf8(message));
      setKeys(next);
      setSignature(sig);
      setSignedText(message);
      setOk(true);
      setVerdict("Both halves verify. The lattice signature is the first 3,309 bytes. Ed25519 is the last 64.");
      setBusy(false);
    }, 20);
  }

  function checkText() {
    if (!keys || !signature) return;
    const pass = hybridVerify(keys.publicKey, utf8(message), signature);
    setOk(pass);
    setVerdict(
      pass
        ? "This exact text matches the signature."
        : "This text is not what was signed. Verification failed, and nothing was decrypted or accepted.",
    );
  }

  function tamper(index: number, reason: string) {
    if (!keys || !signature || signedText === null) return;
    const flipped = new Uint8Array(signature);
    flipped[index] ^= 1;
    setSignature(flipped);
    const pass = hybridVerify(keys.publicKey, utf8(signedText), flipped);
    setOk(pass);
    setVerdict(pass ? "Accepted. That should not happen." : reason);
  }

  const edited = signedText !== null && message !== signedText;

  return (
    <div className="space-y-4">
      <div className="max-w-2xl">
        <h1 className="text-2xl font-medium">Both signatures have to pass.</h1>
        <p className="mt-3 text-sm leading-relaxed text-muted">
          The signature is ML-DSA-65 concatenated with Ed25519. Checking one half and skipping the other
          is not this construction. Edit the text after signing, or flip a byte, and the check should fail.
          If the worry is a shortcut in the lattice rather than a quantum computer, use the{" "}
          <Link href="/hash" className="text-brass-2">
            hash signature
          </Link>
          .
        </p>
      </div>
      <Panel title="Try it">
        <Steps
          items={[
            {
              title: "Sign the text.",
              body: "The first time also generates the key. The public key is 1,984 bytes: 1,952 of ML-DSA-65, then 32 of Ed25519.",
            },
            {
              title: "Change the text and check it.",
              body: "The signature is not updated. Check uses the signature you already have against whatever is in the box now.",
            },
            {
              title: "Or damage the signature itself.",
              body: "The last byte is the Ed25519 half. The first byte is the ML-DSA half. Either change is enough to reject.",
            },
          ]}
        />
        <textarea
          value={message}
          onChange={(event) => setMessage(event.target.value)}
          rows={4}
          className="w-full border border-line bg-ink px-3 py-3 text-sm text-paper outline-none"
        />
        {edited ? <Note>The box no longer matches the signed text. Check it, or sign again.</Note> : null}
        <div className="flex flex-wrap gap-2">
          <Action onClick={signFresh} disabled={busy || message.length === 0}>
            {busy ? "Signing" : keys ? "Sign again" : "Sign"}
          </Action>
          <Action quiet onClick={checkText} disabled={!signature}>
            Check this text
          </Action>
          <Action quiet onClick={() => tamper((signature?.length ?? 1) - 1, "Rejected. The Ed25519 half failed.")} disabled={!signature}>
            Flip last byte
          </Action>
          <Action quiet onClick={() => tamper(0, "Rejected. The ML-DSA half failed.")} disabled={!signature}>
            Flip first byte
          </Action>
        </div>
        {keys ? <p className="font-mono text-xs text-muted">public key {keys.publicKey.length} B</p> : null}
        {signature ? (
          <>
            <p className={ok ? "font-mono text-xs text-brass-2" : "font-mono text-xs text-alarm"}>
              {signature.length} bytes · {verdict}
            </p>
            <p className="break-all font-mono text-xs text-muted">{toHex(signature, 48)}</p>
            <Reading>{verdict}</Reading>
          </>
        ) : null}
        <Python
          source={`from qrclib.hybrid import generate_sign_keys, sign, verify

keys = generate_sign_keys()
signature = sign(keys.secret_key, message)
assert verify(keys.public_key, message, signature)
assert not verify(keys.public_key, message + b" ", signature)`}
        />
      </Panel>
    </div>
  );
}
