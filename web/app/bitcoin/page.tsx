"use client";

import { useState } from "react";
import { Action, Note, Panel } from "@/components/ui";
import { attest, generateWallet, toHex, type BtcWallet } from "@/lib/pq";

const GUIDANCE = [
  "Miners will not see this signature. Consensus still checks secp256k1.",
  "OP_RETURN can carry the 32-byte commitment. The script is 34 bytes. The signature is 3,373.",
  "Once the secp256k1 public key is revealed, a quantum break can still produce a spend miners accept.",
  "Do not reuse addresses. Move the coins when a post-quantum output type actually activates.",
];

export default function Bitcoin() {
  const [wallet, setWallet] = useState<BtcWallet | null>(null);
  const [txid, setTxid] = useState("11".repeat(32));
  const [out, setOut] = useState<{ address: string; sig: number; script: string; ok: boolean } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  function protect() {
    setBusy(true);
    setError(null);
    setTimeout(() => {
      try {
        const next = wallet ?? generateWallet();
        const stamp = new Date().toISOString().replace(/\.\d{3}Z$/, "Z");
        const attestation = attest(next, txid.trim(), stamp);
        setWallet(next);
        setOut({
          address: next.address,
          sig: attestation.signature.length,
          script: toHex(attestation.script),
          ok: attestation.script.length === 34 && attestation.script[0] === 0x6a,
        });
      } catch (err) {
        setError(err instanceof Error ? err.message : "Could not attest");
      } finally {
        setBusy(false);
      }
    }, 20);
  }

  return (
    <div className="space-y-4">
      <div className="max-w-2xl">
        <h1 className="text-2xl font-medium">Bitcoin, without the fairy tale</h1>
        <Note>
          A real compressed secp256k1 key, a real P2PKH address, and a hybrid signature over the txid.
          The thing you can put on chain is the commitment, not the lattice signature.
        </Note>
      </div>
      <Panel title="Attestation">
        <label className="block">
          <span className="mb-1 block text-xs text-muted">Transaction id</span>
          <input
            value={txid}
            onChange={(event) => setTxid(event.target.value)}
            className="w-full border border-line bg-ink px-3 py-3 font-mono text-xs outline-none"
            spellCheck={false}
          />
        </label>
        <Action onClick={protect} disabled={busy}>
          {busy ? "Signing" : "Protect this txid"}
        </Action>
        {error ? <p className="text-sm text-alarm">{error}</p> : null}
        {out ? (
          <dl className="space-y-2 font-mono text-xs">
            <div>
              <dt className="text-muted">P2PKH</dt>
              <dd className="break-all text-paper">{out.address}</dd>
            </div>
            <div>
              <dt className="text-muted">Hybrid signature</dt>
              <dd>{out.sig} B, kept off chain</dd>
            </div>
            <div>
              <dt className="text-muted">OP_RETURN script</dt>
              <dd className={out.ok ? "break-all text-brass-2" : "break-all text-alarm"}>{out.script}</dd>
            </div>
          </dl>
        ) : null}
      </Panel>
      <Panel title="What this does not do">
        <ul className="list-disc space-y-2 pl-5 text-sm text-muted">
          {GUIDANCE.map((line) => (
            <li key={line}>{line}</li>
          ))}
        </ul>
      </Panel>
    </div>
  );
}
