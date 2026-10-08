"use client";

import { useEffect, useState } from "react";
import { Action, Note, Panel } from "@/components/ui";
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
  type HybridSignKeys,
  type XwingKeys,
} from "@/lib/pq";

type Party = { name: string; kem: XwingKeys; sign: HybridSignKeys; key: Uint8Array | null };
type Row = { id: number; from: string; text: string; wire: string };

export default function Messages() {
  const [alice, setAlice] = useState<Party | null>(null);
  const [bob, setBob] = useState<Party | null>(null);
  const [draft, setDraft] = useState("The reading is 18.4 and the agent should not see it in the clear.");
  const [rows, setRows] = useState<Row[]>([]);
  const [next, setNext] = useState<"alice" | "bob">("alice");

  useEffect(() => {
    const aKem = generateXwing();
    const bKem = generateXwing();
    const aSign = generateHybridSign();
    const bSign = generateHybridSign();
    const offer = xwingEncapsulate(bKem.publicKey);
    const offerSig = hybridSign(aSign, offer.ciphertext);
    if (!hybridVerify(aSign.publicKey, offer.ciphertext, offerSig)) return;
    const bobShared = xwingDecapsulate(bKem.secretKey, offer.ciphertext);
    if (!equalBytes(bobShared, offer.shared)) return;
    const key = sessionKey(offer.shared);
    setAlice({ name: "Alice", kem: aKem, sign: aSign, key });
    setBob({ name: "Bob", kem: bKem, sign: bSign, key });
  }, []);

  function send() {
    const from = next === "alice" ? alice : bob;
    if (!from?.key || !draft.trim()) return;
    const packed = encryptMessage(from.key, utf8(draft.trim()));
    const body = concat(packed.nonce, packed.body);
    const signature = hybridSign(from.sign, body);
    const wire = concat(body, signature);
    if (!hybridVerify(from.sign.publicKey, body, signature)) return;
    const opened = decryptMessage(from.key, packed.nonce, packed.body);
    setRows((prev) => [
      ...prev,
      {
        id: prev.length + 1,
        from: from.name,
        text: new TextDecoder().decode(opened),
        wire: `${wire.length} B · ${toHex(wire, 18)}`,
      },
    ]);
    setDraft("");
    setNext(next === "alice" ? "bob" : "alice");
  }

  return (
    <div className="space-y-4">
      <div className="max-w-2xl">
        <h1 className="text-2xl font-medium">Mailbox</h1>
        <Note>
          One X-Wing encapsulation to Bob’s long-term key, then AES-256-GCM. Each packet is hybrid-signed.
          This is not forward secret: a later leak of Bob’s X-Wing secret opens the offer.
        </Note>
      </div>
      <Panel title={alice && bob ? "Session up" : "Bringing the session up"}>
        <p className="font-mono text-xs text-muted">{alice?.key ? `session key ${toHex(alice.key, 8)}` : "waiting"}</p>
        {rows.length === 0 ? <Note>Nothing on the wire yet.</Note> : null}
        {rows.map((row) => (
          <div key={row.id} className="border border-line bg-ink p-3">
            <p className="text-sm">{row.from}</p>
            <p className="mt-1 text-sm">{row.text}</p>
            <p className="mt-2 break-all font-mono text-xs text-muted">{row.wire}</p>
          </div>
        ))}
        <label className="block">
          <span className="mb-1 block text-xs text-muted">From {next === "alice" ? "Alice" : "Bob"}</span>
          <textarea
            value={draft}
            onChange={(event) => setDraft(event.target.value)}
            rows={3}
            className="w-full border border-line bg-ink px-3 py-3 text-sm outline-none"
          />
        </label>
        <Action onClick={send} disabled={!alice || !draft.trim()}>
          Send
        </Action>
      </Panel>
    </div>
  );
}
