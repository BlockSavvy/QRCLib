"use client";

import { useState } from "react";
import { Action, Note, Panel, Reading, Steps } from "@/components/ui";
import { generateSlh, slhSign, slhVerify, toHex, utf8 } from "@/lib/pq";

const bars = [
  ["Ed25519", 64],
  ["Hybrid ML-DSA-65 + Ed25519", 3373],
  ["ML-DSA-87, largest NIST lattice signature", 4627],
  ["SLH-DSA-SHA2-128s, smallest category-1 hash signature", 7856],
  ["SLH-DSA-SHA2-128f, what this page runs", 17088],
] as const;

export default function HashPage() {
  const [message, setMessage] = useState("Authorize settlement 18. No lattice in this signature.");
  const [publicKey, setPublicKey] = useState<Uint8Array | null>(null);
  const [secretKey, setSecretKey] = useState<Uint8Array | null>(null);
  const [signature, setSignature] = useState<Uint8Array | null>(null);
  const [verdict, setVerdict] = useState<string | null>(null);
  const [ok, setOk] = useState<boolean | null>(null);
  const [ms, setMs] = useState<number | null>(null);
  const [busy, setBusy] = useState(false);

  function signFresh() {
    setBusy(true);
    setVerdict(null);
    setTimeout(() => {
      const t0 = performance.now();
      const keys = secretKey && publicKey ? { secretKey, publicKey } : generateSlh();
      const sig = slhSign(keys.secretKey, utf8(message));
      const pass = slhVerify(keys.publicKey, utf8(message), sig);
      setPublicKey(keys.publicKey);
      setSecretKey(keys.secretKey);
      setSignature(sig);
      setOk(pass);
      setMs(performance.now() - t0);
      setVerdict(pass ? "Verified. The check recomputed hashes. It did not use a lattice or a curve." : "Rejected.");
      setBusy(false);
    }, 30);
  }

  function tamper() {
    if (!publicKey || !signature) return;
    const flipped = new Uint8Array(signature);
    flipped[0] ^= 1;
    setSignature(flipped);
    const pass = slhVerify(publicKey, utf8(message), flipped);
    setOk(pass);
    setVerdict(pass ? "Accepted. That should not happen." : "Rejected. One flipped bit was enough.");
  }

  return (
    <div className="space-y-4">
      <div className="max-w-2xl">
        <h1 className="text-2xl font-medium">A signature made only of hashes.</h1>
        <p className="mt-3 text-sm leading-relaxed text-muted">
          SLH-DSA is FIPS 205. This page runs the fast category-1 set, SHA2-128f. The public key is 32 bytes.
          The signature is 17,088. There is no ML-DSA half and no Ed25519 half to fall back on, and nothing to
          take out if someone later finds a shortcut in lattices.
        </p>
      </div>
      <Panel title="Sign with SHA2-128f">
        <Steps
          items={[
            {
              title: "The key is a hash tree, not a trapdoor.",
              body: "Forging it means finding a break in SHA-256, not in a lattice problem and not in an elliptic curve.",
            },
            {
              title: "It is larger than the hybrid, today.",
              body: "The hybrid signature is 3,373 bytes. The largest NIST lattice signature, ML-DSA-87, is 4,627. Even the small hash set, SHA2-128s, is 7,856, and it takes seconds to sign. Hash-based signatures win on assumptions now. They win on size only if lattice parameters have to grow a long way. NIST has not published that growth.",
            },
            {
              title: "Python does not run this yet.",
              body: "cryptography 50 ships ML-KEM and ML-DSA. It does not ship SLH-DSA. This library will not vendor a second implementation while that is true.",
            },
          ]}
        />
        <textarea
          value={message}
          onChange={(event) => setMessage(event.target.value)}
          rows={3}
          className="w-full border border-line bg-ink px-3 py-3 text-sm text-paper outline-none"
        />
        <div className="flex flex-wrap gap-2">
          <Action onClick={signFresh} disabled={busy || message.length === 0}>
            {busy ? "Signing" : secretKey ? "Sign again" : "Sign"}
          </Action>
          <Action quiet onClick={tamper} disabled={!signature}>
            Flip first byte
          </Action>
        </div>
        {busy ? <Note>SHA2-128f is the fast set. A few hundred milliseconds here is normal.</Note> : null}
        {signature && publicKey ? (
          <>
            <p className={ok ? "font-mono text-xs text-brass-2" : "font-mono text-xs text-alarm"}>
              public {publicKey.length} B · signature {signature.length} B
              {ms !== null ? ` · ${ms.toFixed(0)} ms` : ""} · {verdict}
            </p>
            <p className="break-all font-mono text-xs text-muted">{toHex(signature, 32)}</p>
            <Reading>{verdict}</Reading>
          </>
        ) : null}
      </Panel>
      <Panel eyebrow="TODAY" title="Size, not a slogan">
        {bars.map(([label, bytes]) => (
          <Bar key={label} label={label} bytes={bytes} />
        ))}
        <Note>
          A Bitcoin OP_RETURN still holds 80 bytes. Neither signature goes on chain. The 32-byte commitment does.
        </Note>
      </Panel>
    </div>
  );
}

function Bar({ label, bytes }: { label: string; bytes: number }) {
  return (
    <div>
      <div className="mb-1 flex items-baseline justify-between gap-3 text-xs text-muted">
        <span>{label}</span>
        <span className="font-mono">{bytes.toLocaleString()} B</span>
      </div>
      <div className="h-2 bg-panel-2">
        <div className="h-2 bg-brass" style={{ width: `${Math.max(2, Math.round((bytes / 17088) * 100))}%` }} />
      </div>
    </div>
  );
}
