# Distributed Schnorr / BIP340 case-study integration

Integrated on 2026-09-14 into CryptoCave v6.8.

## Canonical article

`src/content/blog/schnorr-js-half-the-time-debugging.md`

Series placement: **Threshold Cryptography Engineering — Part 18**.

## User-source material preserved

- `experiments/threshold-cryptography/schnorr-js-debug/original-snapshot.ts`
- `public/images/blog/schnorr-js-original-network-sketch.png`
- `public/images/blog/schnorr-js-frost-python-sketch.png`
- `public/images/blog/schnorr-js-api-architecture.png`

## Canonical technical result

The recovered experiment is an n-of-n aggregate Schnorr prototype, not FROST. Its main faults were:

1. verification reconstructed `R` as `rG` even though BIP340 encodes `r = x(R)`;
2. signer and verifier used different challenge transcript orderings;
3. aggregate public-key parity was not globally normalized;
4. aggregate nonce parity was not globally normalized;
5. nonce commitments were calculated but not used as a real commit/reveal round;
6. nonce one-time state was not explicit;
7. plain public-key summation lacked rogue-key registration protection; and
8. the v1-era Noble API made later reruns fragile against current package versions.

## Reproducibility

`experiments/threshold-cryptography/schnorr-js-debug/reference-model.mjs` is dependency-free and was executed during consolidation.

Observed validation run:

```text
corrected implementation: 40/40 verified
aggregate-nonce parity fix removed: 54/100 verified (deterministic sample; expected rate ≈50%)
```

`fixed-noble-v2.mjs` targets `@noble/curves@2.4.0` and `@noble/hashes@2.4.0`. Syntax validation passed, but the package could not be installed in the sandbox because external npm installation timed out. Its `npm test` remains a final local check before the article is considered fully runtime-validated against the pinned current Noble release.

## Security label

The corrected code is intentionally described as a **registered-key n-of-n aggregate Schnorr demonstration**. It is not claimed to be MuSig2, FROST, or a production multisignature protocol.
