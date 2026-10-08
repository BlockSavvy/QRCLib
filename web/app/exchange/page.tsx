"use client";

import { useState } from "react";
import { Action, Note, Panel } from "@/components/ui";
import { equalBytes, generateXwing, toHex, xwingDecapsulate, xwingEncapsulate, type XwingKeys } from "@/lib/pq";

export default function Exchange() {
  const [alice, setAlice] = useState<XwingKeys | null>(null);
  const [result, setResult] = useState<{ ct: string; shared: string; match: boolean; ms: number } | null>(null);

  function run() {
    const t0 = performance.now();
    const keys = generateXwing();
    const enc = xwingEncapsulate(keys.publicKey);
    const back = xwingDecapsulate(keys.secretKey, enc.ciphertext);
    setAlice(keys);
    setResult({
      ct: toHex(enc.ciphertext, 24),
      shared: toHex(enc.shared),
      match: equalBytes(back, enc.shared),
      ms: performance.now() - t0,
    });
  }

  return (
    <div className="space-y-4">
      <div className="max-w-2xl">
        <h1 className="text-2xl font-medium">X-Wing</h1>
        <Note>
          ML-KEM-768 plus X25519, following draft-connolly-cfrg-xwing-kem. The shared secret is 32 bytes.
          The ciphertext is 1,120. The public key is 1,216.
        </Note>
      </div>
      <div className="grid gap-4 md:grid-cols-2">
        <Panel eyebrow="ALICE" title="Decapsulation key">
          <p className="font-mono text-xs text-muted">
            public {alice ? `${alice.publicKey.length} B` : "—"}
            <br />
            secret {alice ? `${alice.secretKey.length} B` : "—"}
          </p>
          <Action onClick={run}>Establish</Action>
        </Panel>
        <Panel eyebrow="BOB" title="Encapsulation">
          {result ? (
            <>
              <p className={result.match ? "font-mono text-xs text-brass-2" : "font-mono text-xs text-alarm"}>
                {result.match ? "Shared secrets match" : "Shared secrets differ"} · {result.ms.toFixed(0)} ms
              </p>
              <p className="break-all font-mono text-xs text-muted">ct {result.ct}</p>
              <p className="break-all font-mono text-xs text-paper">ss {result.shared}</p>
            </>
          ) : (
            <Note>Bob has not encapsulated yet.</Note>
          )}
        </Panel>
      </div>
    </div>
  );
}
