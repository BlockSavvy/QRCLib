"use client";

import { useEffect, useState } from "react";
import { Action, Note, Panel } from "@/components/ui";
import { runBench, type Bench } from "@/lib/pq";

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
        <h1 className="text-3xl font-medium tracking-tight">Post-quantum, hybrid by default.</h1>
        <p className="mt-3 text-base leading-relaxed text-muted">
          ML-KEM-768 and ML-DSA-65, each paired with the classical primitive it is replacing.
          Breaking one family is not enough. This page runs in the browser. The Python package is the same construction.
        </p>
      </div>

      <Panel eyebrow="LIVE" title="Self-test in this browser">
        <Note>
          X-Wing key agreement, then a hybrid signature. The old hash stubs are not in this path.
          Keys are discarded when the function returns.
        </Note>
        {bench ? (
          <dl className="grid grid-cols-2 gap-3 font-mono text-xs sm:grid-cols-4">
            <Stat label="Shared secret" value={bench.matched ? "match" : "mismatch"} ok={bench.matched} />
            <Stat label="Tampered sig" value={bench.tamperRejected ? "rejected" : "accepted"} ok={bench.tamperRejected} />
            <Stat label="X-Wing" value={`${bench.kemMs.toFixed(0)} ms`} ok />
            <Stat label="Hybrid sign" value={`${bench.signMs.toFixed(0)} ms`} ok />
          </dl>
        ) : (
          <p className="font-mono text-xs text-brass">{busy ? "Running keygen, encaps, sign…" : "Idle"}</p>
        )}
        {error ? <p className="text-sm text-alarm">{error}</p> : null}
        <Action onClick={go} disabled={busy}>
          {busy ? "Running" : "Run again"}
        </Action>
      </Panel>

      <Panel eyebrow="SIZES" title="Why the hybrid is the annoying part">
        <Size label="Ed25519 signature" bytes={64} max={3373} />
        <Size label="ML-DSA-65 signature" bytes={3309} max={3373} />
        <Size label="Hybrid signature" bytes={3373} max={3373} />
        <Size label="X25519 public key" bytes={32} max={1216} />
        <Size label="X-Wing public key" bytes={1216} max={1216} />
        <Note>
          Bitcoin OP_RETURN holds 80 bytes. The hybrid signature does not fit. The 32-byte commitment does.
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
