"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { Action, Note, Panel, Reading } from "@/components/ui";
import { runBench, type Bench } from "@/lib/pq";

const tour = [
  ["/exchange", "Exchange", "Two parties agree on a secret. Hashes cannot do this part."],
  ["/sign", "Sign", "Lattice plus Ed25519. Both halves must pass. Aimed at a quantum computer."],
  ["/hash", "Hash", "SLH-DSA. No lattice and no curve. Larger today, not smaller."],
  ["/messages", "Mail", "That secret becomes an encrypted session. It is not forward secret."],
  ["/bitcoin", "Bitcoin", "Leave the address unused. Commit 32 bytes. Keep the signature off chain."],
  ["/envelope", "Envelope", "A lattice computation with a short horizon, not archival secrecy."],
];

type Job = "agree" | "sign" | "hide" | "btc";
type Worry = "quantum" | "structure";

const advice: Record<Job, Record<Worry, { href: string; title: string; body: string }>> = {
  agree: {
    quantum: {
      href: "/exchange",
      title: "X-Wing",
      body: "Key agreement needs a trapdoor. Hashes do not provide one. X-Wing stays confidential if either ML-KEM-768 or X25519 holds. The library also speaks ML-KEM-1024. There is no standard parameter set ten times larger, and inventing one would be a new cryptosystem.",
    },
    structure: {
      href: "/exchange",
      title: "Still X-Wing",
      body: "A shortcut in lattices does not create a hash-based replacement for key agreement. The theorem is older than this argument: key agreement does not reduce to one-way functions. Use the hybrid, and treat long-term secrecy as something you rotate.",
    },
  },
  sign: {
    quantum: {
      href: "/sign",
      title: "Hybrid signature",
      body: "ML-DSA-65 is there for a quantum computer. Ed25519 is there in case the lattice fails and the curve does not. Forging it means forging both. The signature is 3,373 bytes.",
    },
    structure: {
      href: "/hash",
      title: "SLH-DSA-SHA2-128f",
      body: "This is the case for a hash signature. It does not use a lattice or a curve. It is 17,088 bytes, so it is the conservative choice, not the compact one. Python cannot run it until cryptography ships FIPS 205.",
    },
  },
  hide: {
    quantum: {
      href: "/envelope",
      title: "Do not archive secrets here",
      body: "CKKS is a lattice. A quantum computer is not what breaks it. An improved lattice estimate might. Use it for a short computation an agent must not read in the clear, then throw the ciphertexts away.",
    },
    structure: {
      href: "/envelope",
      title: "This is the assumption under pressure",
      body: "The envelope is fully homomorphic encryption on a lattice. If that family takes a hit, the envelope takes the hit. It was never a long-term vault. The agent is also assumed not to substitute an answer.",
    },
  },
  btc: {
    quantum: {
      href: "/bitcoin",
      title: "Do not reveal the secp256k1 key",
      body: "An address that has never sent a transaction has not published its public key. When you do spend, miners still check secp256k1. The post-quantum signature stays off chain, behind a 32-byte commitment.",
    },
    structure: {
      href: "/bitcoin",
      title: "Same operational rule",
      body: "Gather a multisig off chain, so the individual signatures are not published. A break then degrades to whoever holds the bundle, not to the whole network. Do not rush a migration to do this.",
    },
  },
};

export default function Home() {
  const [bench, setBench] = useState<Bench | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [job, setJob] = useState<Job>("sign");
  const [worry, setWorry] = useState<Worry>("structure");
  const pick = advice[job][worry];

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
        <h1 className="text-3xl font-medium tracking-tight">Two different threats. Two different locks.</h1>
        <p className="mt-3 text-base leading-relaxed text-muted">
          A quantum computer breaks elliptic curves and leaves hashes and, as far as anyone has proved, lattices.
          A shortcut in the structured math would hit lattices and might hit curves. Those are not the same failure,
          and this site will not pretend one algorithm covers both.
        </p>
      </div>

      <Panel eyebrow="CHOOSE" title="What are you actually doing?">
        <Choice
          label="Job"
          value={job}
          options={[
            ["agree", "Agree on a secret"],
            ["sign", "Sign a message"],
            ["hide", "Hide numbers"],
            ["btc", "Commit a Bitcoin tx"],
          ]}
          onChange={setJob}
        />
        <Choice
          label="Worry"
          value={worry}
          options={[
            ["quantum", "A quantum computer"],
            ["structure", "A shortcut in the math"],
          ]}
          onChange={setWorry}
        />
        <Reading>{pick.body}</Reading>
        <Link href={pick.href} className="inline-flex min-h-11 items-center border border-brass bg-brass px-4 text-sm text-ink">
          {pick.title}
        </Link>
      </Panel>

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
          transaction. The hash signature is larger still, 17,088 bytes. The Bitcoin page puts a 32-byte hash of
          the attestation on chain instead.
        </Note>
      </Panel>
    </div>
  );
}

function Choice<T extends string>({
  label,
  value,
  options,
  onChange,
}: {
  label: string;
  value: T;
  options: [T, string][];
  onChange: (next: T) => void;
}) {
  return (
    <div>
      <p className="mb-2 text-xs text-muted">{label}</p>
      <div className="flex flex-wrap gap-2">
        {options.map(([id, text]) => (
          <button
            key={id}
            type="button"
            onClick={() => onChange(id)}
            className={
              value === id
                ? "min-h-11 border border-brass bg-brass px-3 text-sm text-ink"
                : "min-h-11 border border-line bg-ink px-3 text-sm text-paper"
            }
          >
            {text}
          </button>
        ))}
      </div>
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
