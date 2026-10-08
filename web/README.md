# QRCLib web demo

Next.js app deployed at [pqcl.aiya.sh](https://pqcl.aiya.sh).

`/examples/basic` calls `/api/crypto/*`, which uses ML-DSA-65 from `@noble/post-quantum`.
That is the same signature algorithm as `qrclib.dsa` in the Python package.
The other example pages are illustrations and are not a wallet, a chain, or a mailbox.

```bash
npm install
npm run dev
```
