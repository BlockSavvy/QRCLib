"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { Action, Note, Panel, Reading } from "@/components/ui";
import { runBench, type Bench } from "@/lib/pq";

const tour = [
  ["/exchange", "Exchange", "Two parties agree on a secret without sending it."],
  ["/sign", "Sign", "A signature that needs both a lattice and Ed25519 to pass."],
  ["/messages", "Mail", "That secret becomes an encrypted session. It is not forward secret."],
  ["/bitcoin", "Bitcoin", "The signature is too big for a transaction. A 32-byte commitment is not."],
  ["/envelope", "Envelope", "Sums on encrypted numbers. That part runs in Python, not here."],
];

export default function Home() {
  const [bench, setBench] = useState<Bench | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  function go() {
    setBusy(true);
    setError(null);
    setTimeout(() => {
      try {
        setBench(runBench());
      } catch (err) {
        setError(err instanceof Error ? err.message : "Bench failed");
      } finally {
        setBusy(false);
      }
    }, 30);
  }

  useEffect(() => {
    go();
  }, []);

  return (
    <div className="space-y-6">
      <div className="max-w-2xl">
        <h1 className="text-3xl font-medium tracking-tight">Two locks on every door.</h1>
        <p className="mt-3 text-base leading-relaxed text-muted">
          Each operation pairs a post-quantum algorithm with the classical one it is meant to replace.
          A break of only one family is not enough. Nothing on this site is a simulation of the math.
          The browser runs the same constructions as the Python library.
        </p>
      </div>

      <Panel eyebrow="TOUR" title="What the other pages do">
        <ul className="space-y-3">
          {tour.map(([href, label, line]) => (
            <li key={href}>
              <Link href={href} className="text-sm text-brass-2">
                {label}
              </Link>
              <p className="mt-1 text-sm leading-relaxed text-muted">{line}</p>
            </li>
          ))}
        </ul>
      </Panel>

      <Panel eyebrow="IN THIS BROWSER" title="A key agreement, then a signature">
        <Note>
          Pressing the button creates an X-Wing key, encapsulates a secret, decapsulates it, and signs
          a short message. It then flips one bit of the signature. Keys are thrown away when the function returns.
          The first run on a phone can take a few seconds. That is ML-DSA key generation, not a stall.
        </Note>
        {bench ? (
          <>
            <dl className="grid grid-cols-2 gap-3 font-mono text-xs sm:grid-cols-4">
              <Stat label="Shared secret" value={bench.matched ? "match" : "mismatch"} ok={bench.matched} />
              <Stat label="Flipped bit" value={bench.tamperRejected ? "rejected" : "accepted"} ok={bench.tamperRejected} />
              <Stat label="X-Wing" value={`${bench.kemMs.toFixed(0)} ms`} ok />
              <Stat label="Hybrid sign" value={`${bench.signMs.toFixed(0)} ms`} ok />
            </dl>
            <Reading>
              {bench.matched
                ? "Match means both sides computed the same 32-byte secret. It was never placed in the ciphertext."
                : "Mismatch means the two sides disagreed. That is a bug, not a feature."}{" "}
              {bench.tamperRejected
                ? "Rejected means changing one bit of the signature made verification fail."
                : "The flipped signature was accepted. That should not happen."}{" "}
              The times are this browser, not a server.
            </Reading>
          </>
        ) : (
          <p className="font-mono text-xs text-brass">{busy ? "Generating keys and signing…" : "Idle"}</p>
        )}
        {error ? <p className="text-sm text-alarm">{error}</p> : null}
        <Action onClick={go} disabled={busy}>
          {busy ? "Running" : "Run again"}
        </Action>
      </Panel>

      <Panel eyebrow="SIZES" title="The hybrid is mostly the lattice half">
        <Size label="Ed25519 signature" bytes={64} max={3373} />
        <Size label="ML-DSA-65 signature" bytes={3309} max={3373} />
        <Size label="Hybrid signature" bytes={3373} max={3373} />
        <Size label="X25519 public key" bytes={32} max={1216} />
        <Size label="X-Wing public key" bytes={1216} max={1216} />
        <Note>
          A Bitcoin OP_RETURN output holds 80 bytes. The hybrid signature is 3,373 bytes, so it cannot go in the
          transaction. The Bitcoin page puts a 32-byte hash of it on chain instead.
        </Note>
      </Panel>
    </div>
  );
}

function Stat({ label, value, ok }: { label: string; value: string; ok: boolean }) {
  return (
    <div className="border border-line bg-ink p-3">
      <dt className="text-muted">{label}</dt>
      <dd className={ok ? "mt-1 text-brass-2" : "mt-1 text-alarm"}>{value}</dd>
    </div>
  );
}

function Size({ label, bytes, max }: { label: string; bytes: number; max: number }) {
  const width = Math.max(2, Math.round((bytes / max) * 100));
  return (
    <div>
      <div className="mb-1 flex items-baseline justify-between gap-3 text-xs text-muted">
        <span>{label}</span>
        <span className="font-mono">{bytes} B</span>
      </div>
      <div className="h-2 bg-panel-2">
        <div className="h-2 bg-brass" style={{ width: `${width}%` }} />
      </div>
    </div>
  );
}
