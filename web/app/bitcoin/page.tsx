"use client";

import { useState } from "react";
import { Action, Note, Panel, Python, Reading, Steps } from "@/components/ui";
import { attest, equalBytes, generateWallet, toHex, type BtcWallet } from "@/lib/pq";

export default function Bitcoin() {
  const [wallet, setWallet] = useState<BtcWallet | null>(null);
  const [txid, setTxid] = useState("11".repeat(32));
  const [out, setOut] = useState<{
    address: string;
    sig: number;
    script: string;
    commitment: string;
    carries: boolean;
  } | null>(null);
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
        const payload = attestation.script.subarray(2);
        setWallet(next);
        setOut({
          address: next.address,
          sig: attestation.signature.length,
          script: toHex(attestation.script),
          commitment: toHex(attestation.commitment),
          carries: attestation.script.length === 34 && attestation.script[0] === 0x6a && attestation.script[1] === 0x20 && equalBytes(payload, attestation.commitment),
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
        <h1 className="text-2xl font-medium">Commit on chain. Keep the signature off it.</h1>
        <p className="mt-3 text-sm leading-relaxed text-muted">
          Bitcoin miners still require a secp256k1 signature to spend coins. This page makes a normal
          P2PKH address, then a hybrid signature over the transaction id. Only a hash of that attestation
          is small enough for an OP_RETURN output.
        </p>
      </div>
      <Panel title="Protect one transaction id">
        <Steps
          items={[
            {
              title: "A compressed secp256k1 key becomes a P2PKH address.",
              body: "That address is spendable under today’s consensus rules. The hybrid key sitting next to it is not a Bitcoin output type.",
            },
            {
              title: "The hybrid signature covers the txid, both public keys, and a timestamp.",
              body: "It is 3,373 bytes. You keep it, and the signed statement, wherever you keep records. Miners never see it.",
            },
            {
              title: "The chain gets 34 bytes of script.",
              body: "6a is OP_RETURN. 20 says the next 32 bytes are data. Those 32 bytes are SHA-256 of the statement plus the signature.",
            },
          ]}
        />
        <label className="block">
          <span className="mb-1 block text-xs text-muted">Transaction id, 64 hex characters</span>
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
          <>
            <dl className="space-y-2 font-mono text-xs">
              <div>
                <dt className="text-muted">P2PKH address, spendable with secp256k1</dt>
                <dd className="break-all text-paper">{out.address}</dd>
              </div>
              <div>
                <dt className="text-muted">Hybrid signature, kept off chain</dt>
                <dd>{out.sig} B</dd>
              </div>
              <div>
                <dt className="text-muted">Commitment inside the script</dt>
                <dd className="break-all">{out.commitment}</dd>
              </div>
              <div>
                <dt className="text-muted">OP_RETURN script</dt>
                <dd className={out.carries ? "break-all text-brass-2" : "break-all text-alarm"}>{out.script}</dd>
              </div>
            </dl>
            <Reading>
              {out.carries
                ? "The script is OP_RETURN, a 32-byte push, and that push is the commitment. Anyone with the off-chain signature can recompute the hash and see that it matches. Anyone with only the chain cannot recover the signature."
                : "The script does not match the commitment. Do not treat this attestation as well-formed."}
            </Reading>
          </>
        ) : (
          <Note>No attestation yet. The address is created the first time you protect a txid.</Note>
        )}
        <Note>
          This does not make the coins quantum-safe. An address that has never sent a transaction has not
          published its secp256k1 key, and that is the exposure to avoid. After the key is revealed, a break
          of that curve can still produce a spend that miners accept. Gather a multisig off chain so the
          individual signatures are not published. Do not rush a migration to get there. Move the coins when
          a post-quantum output type exists, and do not reuse the address.
        </Note>
        <Python
          source={`from qrclib.bitcoin import QuantumProtectedWallet

wallet = QuantumProtectedWallet.generate()
attestation = wallet.protect_transaction("11" * 32)
assert attestation.verify()
script = attestation.op_return_script()
assert script[:2] == bytes.fromhex("6a20")
assert len(script) == 34`}
        />
      </Panel>
    </div>
  );
}
