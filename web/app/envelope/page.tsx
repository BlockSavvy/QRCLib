import { Note, Panel } from "@/components/ui";

export default function Envelope() {
  return (
    <div className="space-y-4">
      <div className="max-w-2xl">
        <h1 className="text-2xl font-medium">Lattice envelope</h1>
        <Note>
          CKKS runs in Python, through TenSEAL. This site does not pretend to evaluate ciphertexts in the browser.
          The agent is assumed semi-honest. The numbers are approximate.
        </Note>
      </div>
      <Panel eyebrow="OPTIONAL" title="What the package actually does">
        <Note>
          X-Wing wraps the secret context. A hybrid signature covers the policy. The agent receives the public
          context only and can be asked for a sum or a mean. It can substitute a result, and the recipient cannot
          tell from the cryptography alone.
        </Note>
        <dl className="grid gap-3 font-mono text-xs sm:grid-cols-2">
          <Fact label="Scheme" value="CKKS" />
          <Fact label="Polynomial degree" value="8192" />
          <Fact label="Moduli" value="50, 30, 50" />
          <Fact label="Scale" value="2^30" />
          <Fact label="Values" value="at most 16" />
          <Fact label="Forward secrecy" value="no" />
        </dl>
        <pre className="overflow-x-auto border border-line bg-ink p-3 font-mono text-xs text-brass-2">{`pip install -e '.[fhe]'
python examples/lhe_example.py`}</pre>
      </Panel>
      <Panel title="What was removed from this site">
        <Note>
          The old pages claimed a quantum-resistant blockchain, file vault, and API gateway. Those were sketches
          on top of hash stand-ins. They are gone. The mailbox, the signature, and the Bitcoin commitment on this
          site use the same hybrids as the library.
        </Note>
      </Panel>
    </div>
  );
}

function Fact({ label, value }: { label: string; value: string }) {
  return (
    <div className="border border-line bg-ink p-3">
      <dt className="text-muted">{label}</dt>
      <dd className="mt-1 text-paper">{value}</dd>
    </div>
  );
}
