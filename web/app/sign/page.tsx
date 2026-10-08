"use client";

import { useState } from "react";
import { Action, Note, Panel } from "@/components/ui";
import { generateHybridSign, hybridSign, hybridVerify, toHex, utf8, type HybridSignKeys } from "@/lib/pq";

export default function SignPage() {
  const [message, setMessage] = useState("Authorize settlement 18 for the data market.");
  const [keys, setKeys] = useState<HybridSignKeys | null>(null);
  const [signature, setSignature] = useState<Uint8Array | null>(null);
  const [verdict, setVerdict] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  function signFresh() {
    setBusy(true);
    setVerdict(null);
    setTimeout(() => {
      const next = keys ?? generateHybridSign();
      const sig = hybridSign(next, utf8(message));
      setKeys(next);
      setSignature(sig);
      setVerdict(hybridVerify(next.publicKey, utf8(message), sig) ? "Both halves verify." : "Rejected.");
      setBusy(false);
    }, 20);
  }

  function tamper(index: number, label: string) {
    if (!keys || !signature) return;
    const flipped = new Uint8Array(signature);
    flipped[index] ^= 1;
    setSignature(flipped);
    setVerdict(hybridVerify(keys.publicKey, utf8(message), flipped) ? "Accepted." : label);
  }

  return (
    <div className="space-y-4">
      <div className="max-w-2xl">
        <h1 className="text-2xl font-medium">Hybrid signature</h1>
        <Note>
          ML-DSA-65 (3,309 bytes) concatenated with Ed25519 (64). Both must verify. Kyber and Dilithium
          names in the Python package are aliases for these FIPS bytes, not Round-3 wire formats.
        </Note>
      </div>
      <Panel title="Message">
        <textarea
          value={message}
          onChange={(event) => setMessage(event.target.value)}
          rows={4}
          className="w-full border border-line bg-ink px-3 py-3 text-sm text-paper outline-none"
        />
        <div className="flex flex-wrap gap-2">
          <Action onClick={signFresh} disabled={busy || message.length === 0}>
            {busy ? "Signing" : "Sign"}
          </Action>
          <Action quiet onClick={() => tamper(signature ? signature.length - 1 : 0, "Rejected. Ed25519 half failed.")} disabled={!signature}>
            Flip last byte
          </Action>
          <Action quiet onClick={() => tamper(0, "Rejected. ML-DSA half failed.")} disabled={!signature}>
            Flip first byte
          </Action>
        </div>
        {keys ? (
          <p className="font-mono text-xs text-muted">public key {keys.publicKey.length} B</p>
        ) : null}
        {signature ? (
          <>
            <p className="font-mono text-xs text-brass-2">
              {signature.length} bytes · {verdict}
            </p>
            <p className="break-all font-mono text-xs text-muted">{toHex(signature, 48)}</p>
          </>
        ) : null}
      </Panel>
    </div>
  );
}
