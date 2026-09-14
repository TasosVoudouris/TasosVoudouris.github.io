# Distributed Schnorr Debugging Case Study

This directory accompanies the CryptoCave article **When Schnorr Worked Only Half the Time**.

It has three layers:

- `original-snapshot.ts` — the recovered TypeScript experiment, preserved for forensic comparison.
- `reference-model.mjs` — dependency-free secp256k1/BIP340 model used in CryptoCave validation.
- `fixed-noble-v2.mjs` — the cleaned implementation targeting `@noble/curves@2.4.0`.
- `test-noble.mjs` — 100 fixed signing sessions plus a deliberate parity-regression experiment.

## Run the dependency-free reference model

```bash
node reference-model.mjs
```

## Run the current Noble implementation

Node 20.19+ is required by Noble v2; CryptoCave itself recommends Node 24.

```bash
npm install
npm run demo
npm test
```

Expected behavior:

- the corrected implementation verifies every test session;
- deliberately removing the aggregate-nonce parity correction produces a success rate near 50% when the aggregate public key is kept fixed.

## Security scope

This is an educational **registered-key n-of-n aggregate Schnorr** experiment. It is not FROST and is not a substitute for BIP327 MuSig2. For production multi-signatures use a reviewed MuSig2 implementation; for threshold Schnorr use an RFC 9591 FROST implementation.
