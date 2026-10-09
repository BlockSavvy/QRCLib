"use client";

import { useState } from "react";
import { Action, Note, Panel, Python, Reading, Steps } from "@/components/ui";
import { equalBytes, generateXwing, toHex, xwingDecapsulate, xwingEncapsulate, type XwingKeys } from "@/lib/pq";

export default function Exchange() {
  const [alice, setAlice] = useState<XwingKeys | null>(null);
  const [result, setResult] = useState<{ ct: number; shared: string; match: boolean; ms: number } | null>(null);

  function run() {
    const t0 = performance.now();
    const keys = generateXwing();
    const enc = xwingEncapsulate(keys.publicKey);
    const back = xwingDecapsulate(keys.secretKey, enc.ciphertext);
    setAlice(keys);
    setResult({
      ct: enc.ciphertext.length,
      shared: toHex(enc.shared),
      match: equalBytes(back, enc.shared),
      ms: performance.now() - t0,
    });
  }

  return (
    <div className="space-y-4">
      <div className="max-w-2xl">
        <h1 className="text-2xl font-medium">Agree on a secret that is never sent.</h1>
        <p className="mt-3 text-sm leading-relaxed text-muted">
          Alice publishes a public key. Bob uses it to create a ciphertext and a 32-byte secret.
          Alice uses her private key on that ciphertext and gets the same secret. This is X-Wing:
          ML-KEM-768 and X25519, combined so that both have to be broken.
        </p>
      </div>
      <Panel title="What Establish does">
        <Steps
          items={[
            {
              title: "Alice generates a 32-byte seed.",
              body: "SHAKE256 stretches it into an ML-KEM-768 key and an X25519 key. The public key you will see is 1,216 bytes: 1,184 of lattice, then 32 of X25519.",
            },
            {
              title: "Bob encapsulates to that public key.",
              body: "He gets an ML-KEM ciphertext (1,088 bytes) and an X25519 ephemeral public key (32 bytes). Those 1,120 bytes are what he sends. The secret stays local.",
            },
            {
              title: "Both sides run the same combiner.",
              body: "SHA3-256 over the two shared secrets, Bob’s ephemeral key, Alice’s X25519 key, and a fixed label. If the digests match, the exchange worked.",
            },
          ]}
        />
        <Action onClick={run}>Establish</Action>
        {alice && result ? (
          <>
            <p className="font-mono text-xs text-muted">
              Alice public {alice.publicKey.length} B · secret {alice.secretKey.length} B · ciphertext {result.ct} B · {result.ms.toFixed(0)} ms
            </p>
            <p className="break-all font-mono text-xs text-paper">shared secret {result.shared}</p>
            <Reading>
              {result.match
                ? "The two sides computed the same 32 bytes. Look at the ciphertext size above: the secret is not sitting inside it."
                : "The two sides disagreed. Treat that as a failure of this page, not as a successful exchange."}
            </Reading>
          </>
        ) : (
          <Note>Nothing has been exchanged yet.</Note>
        )}
        <Python
          source={`from qrclib.hybrid import generate_kem_keys, encapsulate, decapsulate

alice = generate_kem_keys()
ciphertext, bob = encapsulate(alice.public_key)
alice_copy = decapsulate(alice.secret_key, ciphertext)
assert alice_copy == bob`}
        />
      </Panel>
    </div>
  );
}
