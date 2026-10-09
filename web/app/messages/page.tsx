"use client";

import { useEffect, useState } from "react";
import { Action, Note, Panel, Python, Reading, Steps } from "@/components/ui";
import {
  concat,
  decryptMessage,
  encryptMessage,
  equalBytes,
  generateHybridSign,
  generateXwing,
  hybridSign,
  hybridVerify,
  sessionKey,
  toHex,
  utf8,
  xwingDecapsulate,
  xwingEncapsulate,
  SIZES,
  type HybridSignKeys,
} from "@/lib/pq";

type Party = { name: string; sign: HybridSignKeys; key: Uint8Array; peerPublic: Uint8Array };
type Row = { id: number; from: string; text: string; wire: string; ok: boolean };

function openPacket(receiver: Party, wire: Uint8Array): { ok: true; text: string } | { ok: false; reason: string } {
  if (wire.length < SIZES.hybridSig + 12 + 16) {
    return { ok: false, reason: "The packet is too short to be a message." };
  }
  const body = wire.subarray(0, wire.length - SIZES.hybridSig);
  const signature = wire.subarray(wire.length - SIZES.hybridSig);
  if (!hybridVerify(receiver.peerPublic, body, signature)) {
    return { ok: false, reason: "The receiver rejected the signature, so the ciphertext was not opened." };
  }
  try {
    const opened = decryptMessage(receiver.key, body.subarray(0, 12), body.subarray(12));
    return { ok: true, text: new TextDecoder().decode(opened) };
  } catch {
    return { ok: false, reason: "The signature passed, but AES-GCM rejected the ciphertext." };
  }
}

export default function Messages() {
  const [alice, setAlice] = useState<Party | null>(null);
  const [bob, setBob] = useState<Party | null>(null);
  const [draft, setDraft] = useState("The reading is 18.4 and the agent should not see it in the clear.");
  const [rows, setRows] = useState<Row[]>([]);
  const [last, setLast] = useState<{ wire: Uint8Array; to: "alice" | "bob" } | null>(null);
  const [next, setNext] = useState<"alice" | "bob">("alice");
  const [notice, setNotice] = useState<string | null>(null);

  useEffect(() => {
    const bKem = generateXwing();
    const aSign = generateHybridSign();
    const bSign = generateHybridSign();
    const offer = xwingEncapsulate(bKem.publicKey);
    const offerSig = hybridSign(aSign, offer.ciphertext);
    if (!hybridVerify(aSign.publicKey, offer.ciphertext, offerSig)) return;
    const bobShared = xwingDecapsulate(bKem.secretKey, offer.ciphertext);
    if (!equalBytes(bobShared, offer.shared)) return;
    const key = sessionKey(offer.shared);
    setAlice({ name: "Alice", sign: aSign, key, peerPublic: bSign.publicKey });
    setBob({ name: "Bob", sign: bSign, key, peerPublic: aSign.publicKey });
  }, []);

  function send() {
    const from = next === "alice" ? alice : bob;
    const to = next === "alice" ? bob : alice;
    if (!from || !to || !draft.trim()) return;
    const packed = encryptMessage(from.key, utf8(draft.trim()));
    const body = concat(packed.nonce, packed.body);
    const signature = hybridSign(from.sign, body);
    const wire = concat(body, signature);
    const opened = openPacket(to, wire);
    if (!opened.ok) {
      setNotice(opened.reason);
      return;
    }
    setNotice(null);
    setLast({ wire, to: next === "alice" ? "bob" : "alice" });
    setRows((prev) => [
      ...prev,
      { id: prev.length + 1, from: from.name, text: opened.text, wire: `${wire.length} B · ${toHex(wire, 18)}`, ok: true },
    ]);
    setDraft("");
    setNext(next === "alice" ? "bob" : "alice");
  }

  function corrupt() {
    if (!last || !alice || !bob) return;
    const damaged = new Uint8Array(last.wire);
    damaged[12] ^= 1;
    const receiver = last.to === "bob" ? bob : alice;
    const opened = openPacket(receiver, damaged);
    setNotice(opened.ok ? "The damaged packet was accepted. That should not happen." : opened.reason);
    setRows((prev) => [
      ...prev,
      {
        id: prev.length + 1,
        from: "Damaged packet",
        text: opened.ok ? opened.text : opened.reason,
        wire: "one bit flipped inside the ciphertext",
        ok: opened.ok,
      },
    ]);
  }

  return (
    <div className="space-y-4">
      <div className="max-w-2xl">
        <h1 className="text-2xl font-medium">Encrypt, then prove who sent it.</h1>
        <p className="mt-3 text-sm leading-relaxed text-muted">
          Alice encapsulates to Bob’s long-term X-Wing key. Both sides turn that shared secret into an
          AES-256-GCM key. Every packet is hybrid-signed, and the receiver checks the signature before decrypting.
        </p>
      </div>
      <Panel title={alice && bob ? "Session is up" : "Bringing the session up"}>
        <Steps
          items={[
            {
              title: "The offer is a single X-Wing encapsulation.",
              body: "It is signed so Bob knows it came from Alice. Both sides then run HKDF to get the session key. You only see the first eight bytes of that key.",
            },
            {
              title: "A message is a nonce, a ciphertext, and a signature.",
              body: "The other party verifies with the sender’s public key. Only then does AES-GCM open it. Changing the text in flight fails that check.",
            },
            {
              title: "This is not forward secret.",
              body: "If Bob’s long-term X-Wing secret leaks later, the recorded offer can be decapsulated and the session key recomputed. Rotating that key is what bounds the window.",
            },
          ]}
        />
        <p className="font-mono text-xs text-muted">
          {alice ? `session key ${toHex(alice.key, 8)}` : "waiting on key generation"}
        </p>
        {rows.length === 0 ? <Note>Nothing has been delivered yet.</Note> : null}
        {rows.map((row) => (
          <div key={row.id} className="border border-line bg-ink p-3">
            <p className="text-sm">{row.from}</p>
            <p className={row.ok ? "mt-1 text-sm" : "mt-1 text-sm text-alarm"}>{row.text}</p>
            <p className="mt-2 break-all font-mono text-xs text-muted">{row.wire}</p>
          </div>
        ))}
        {notice ? <Reading>{notice}</Reading> : null}
        <label className="block">
          <span className="mb-1 block text-xs text-muted">From {next === "alice" ? "Alice" : "Bob"}</span>
          <textarea
            value={draft}
            onChange={(event) => setDraft(event.target.value)}
            rows={3}
            className="w-full border border-line bg-ink px-3 py-3 text-sm outline-none"
          />
        </label>
        <div className="flex flex-wrap gap-2">
          <Action onClick={send} disabled={!alice || !draft.trim()}>
            Send
          </Action>
          <Action quiet onClick={corrupt} disabled={!last}>
            Corrupt the last packet
          </Action>
        </div>
        <Python
          source={`from qrclib.messaging import Mailbox

alice, bob = Mailbox("alice"), Mailbox("bob")
bob.accept(alice.offer(bob.kem.public_key), alice.signing.public_key)
alice.bind_peer(bob.signing.public_key)
print(bob.decrypt(alice.encrypt(b"18.4")))`}
        />
      </Panel>
    </div>
  );
}
