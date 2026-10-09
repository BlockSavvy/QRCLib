import { Note, Panel, Python, Steps } from "@/components/ui";

export default function Envelope() {
  return (
    <div className="space-y-4">
      <div className="max-w-2xl">
        <h1 className="text-2xl font-medium">The agent can add the numbers and still not read them.</h1>
        <p className="mt-3 text-sm leading-relaxed text-muted">
          CKKS is approximate encryption for real numbers. Sums and means run on the ciphertexts.
          This page does not run that math. TenSEAL is a native library, and pretending to evaluate it
          in the browser would teach the wrong thing.
        </p>
      </div>
      <Panel title="Three parties">
        <Steps
          items={[
            {
              title: "The owner encrypts up to sixteen numbers.",
              body: "The CKKS parameters are a polynomial degree of 8192, moduli of 50, 30, and 50 bits, and a scale of 2^30. The result is close to the plaintext, not identical.",
            },
            {
              title: "The agent receives the public context only.",
              body: "It may compute a sum, a mean, a shift, a scale, or a plaintext mask. It does not receive the secret that opens the column. It can still substitute a different result, and CKKS will not tell the recipient that happened.",
            },
            {
              title: "The recipient opens it with a key that was sealed to them.",
              body: "X-Wing wraps the secret context. A hybrid signature covers the policy, so an outsider cannot widen what the agent was allowed to do. The signature does not make the agent honest.",
            },
          ]}
        />
        <Note>
          The same limit as the mailbox applies to the wrapped secret: this envelope is not forward secret.
          A later leak of the recipient’s X-Wing key opens recorded envelopes.
        </Note>
        <Python
          source={`# pip install 'qrclib[fhe]'
from qrclib.lhe import seal, evaluate, open_result
# see examples/lhe_example.py for the key setup
# the homomorphic mean is within about 0.001 of the plaintext mean`}
        />
      </Panel>
      <Panel title="What this site used to claim">
        <Note>
          The earlier demo had a blockchain, a file vault, and an API gateway. Those pages hashed stand-ins and
          called the result quantum-resistant. They are gone. The four interactive pages before this one run the
          real hybrid. This one tells you where the homomorphic part actually runs.
        </Note>
      </Panel>
    </div>
  );
}
