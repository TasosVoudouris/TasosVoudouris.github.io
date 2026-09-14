# Threshold cryptography integration map

Source batch: `rdy.zip`.

## Editorial decisions

The material was not copied as one flat group. It was normalized into one ordered series plus one primer article:

### Cryptography Primer addition
- Randomness in Cryptography: Entropy, CSPRNGs, and Operating-System Randomness

### Secret Sharing & Threshold Cryptography
1. Additive Secret Sharing: Linear Sharing over Finite Fields
2. Shamir's Secret Sharing: Lagrange Interpolation and Perfect Privacy
3. Finite-Field Polynomial Interpolation: Lagrange, Newton, Barycentric, and FFT Methods
4. Packed Secret Sharing: Encoding Multiple Secrets in One Polynomial
5. Polynomial Splitting and Roots of Unity: From Horner's Rule to FFT Structure
6. FFT-Based Packed Secret Sharing over Finite Fields
7. Robust Secret Sharing: Reed-Solomon Codes and Gao Decoding
8. From Verifiable Secret Sharing to Pedersen-Style DKG
9. Aggregatable DKG and SCRAPE-Style PVSS: A Scalability Research Note
10. Secret Sharing, Multisignatures, BLS Aggregation, DKG, and Threshold Signatures Compared
11. Distributed Randomness Beacons: DKG, Threshold BLS, and Public Verifiability

## Important source splits

`Randomness.md` contained two distinct subjects and was split into:
- local cryptographic randomness / entropy / CSPRNGs;
- distributed randomness beacons.

`DKG.md` contained two major protocol blocks and was split into:
- VSS and Pedersen-style DKG;
- aggregatable DKG / SCRAPE-style PVSS.

The original source notes are preserved under:

```text
research-notes/threshold-cryptography/original-rdy/
```

## Technical corrections made

- Clarified that packed-sharing point signs are a coding convention, not a requirement.
- Corrected the packed polynomial degree to `K + T - 1` / degree `< ORDER2` where applicable.
- Clarified privacy-threshold wording.
- Distinguished single-point Lagrange evaluation from full-polynomial interpolation complexity.
- Distinguished multisignatures, aggregate signatures, DKG, and threshold signatures.
- Replaced over-broad DKG fault-threshold claims with protocol/model-specific wording.
- Separated Shannon entropy from min-entropy and corrected entropy-combination statements.
- Modernized OS CSPRNG guidance and removed outdated SSL-era explanations.
- Documented the missing `FFTonly` module in the recovered benchmark bundle instead of fabricating it.
- Rebuilt dependency-free educational implementations for additive, Shamir, packed, polynomial-splitting, and FFT-packed sharing.

## Validation

The dependency-free implementations are exercised by:

```bash
python experiments/threshold-cryptography/run_all.py
```

SageMath interpolation benchmark sources and original plots are preserved separately and are not represented as a platform-independent test suite.
