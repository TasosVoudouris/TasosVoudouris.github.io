# Secret sharing and the road to threshold cryptography

This chapter series accompanies CryptoCave Threshold Cryptography Version 0.5.
It develops the algebraic foundation, Feldman and Pedersen VSS, explicit
protocol/session states, an offline multi-dealer DKG layer, and a two-round
threshold Schnorr/FROST signing lesson.

## Reading order

1. [Finite fields and polynomials](01-finite-fields-and-polynomials.md)
2. [Additive secret sharing](02-additive-secret-sharing.md)
3. [Shamir secret sharing](03-shamir-secret-sharing.md)
4. [Arithmetic and multiplication](04-arithmetic-and-multiplication.md)
5. [Consistency and robust reconstruction](05-consistency-and-robust-reconstruction.md)
6. [Packed ramp sharing and the NTT](06-packed-ramp-sharing-and-ntt.md)
7. [Security boundaries and development roadmap](07-security-boundaries-and-roadmap.md)
8. [Why ordinary Shamir sharing is not enough](08-from-shamir-to-vss.md)
9. [Feldman verifiable secret sharing](09-feldman-vss.md)
10. [Broadcast, complaints, and the protocol boundary](10-vss-protocol-boundary.md)
11. [Audit of the original VSS experiments](11-original-vss-code-audit.md)
12. [Pedersen verifiable secret sharing](12-pedersen-vss.md)
13. [Feldman and Pedersen compared](13-feldman-vs-pedersen.md)
14. [VSS sessions, transcripts, and broadcast](14-vss-session-and-broadcast.md)
15. [Complaints, qualification, and abort](15-complaints-qualification-and-abort.md)
16. [Version 0.3 security boundary](16-version-03-security-boundary.md)
17. [From VSS to distributed key generation](17-from-vss-to-dkg.md)
18. [The Version 0.4 multi-dealer construction](18-multi-dealer-dkg.md)
19. [Qualification, public-key derivation, and audit](19-dkg-qualification-and-public-key.md)
20. [DKG failure cases and adversarial lessons](20-dkg-failure-cases.md)
21. [Version 0.4 security boundary](21-version-04-security-boundary.md)
22. [From DKG output to a threshold signature](22-from-dkg-to-threshold-signatures.md)
23. [Schnorr algebra and threshold interpolation](23-schnorr-and-threshold-interpolation.md)
24. [The RFC 9591 two-round FROST protocol](24-rfc9591-frost-protocol.md)
25. [Version 0.5 code walkthrough](25-version-05-code-walkthrough.md)
26. [Nonces, validation, replay boundaries, and failure](26-nonces-validation-and-failure.md)
27. [RFC 9591 conformance and deviation map](27-rfc9591-conformance-map.md)
28. [Version 0.5 security boundary](28-version-05-security-boundary.md)
29. [References](references.md)

Each page distinguishes:

- the mathematical equation;
- the guarantee under stated assumptions;
- what the Version 0.5 code implements;
- what a distributed or production protocol still requires.

## Version 0.5 at a glance

| Mechanism | Implemented? | Present guarantee | Missing next layer |
|---|---:|---|---|
| Additive sharing | Yes | Privacy against every strict subset in N-out-of-N sharing | Authentication and malicious security |
| Shamir sharing | Yes | Threshold privacy and exact reconstruction in the passive model | VSS/DKG protocol integration |
| Linear share arithmetic | Yes | Correct local addition, subtraction, and public scaling | Authenticated shares |
| Pointwise multiplication | Lesson | Correct evaluations with explicit degree growth | Degree reduction or MPC multiplication |
| Beaver multiplication | Lesson | Passive multiplication with trusted preprocessing | Secure authenticated triple generation |
| Robust reconstruction | Small decoder | Bounded correction with sufficient redundancy | Scalable Reed–Solomon decoder |
| Packed ramp sharing | Yes | Exact 3/4/7/8 ramp profile of the original construction | Protocol integration |
| Feldman verification | Yes | Detects inconsistency with one non-hiding commitment vector | Common broadcast and authentication |
| Pedersen verification | Yes | Hiding coefficient commitments in the mathematical toy model | Production generators and group library |
| VSS session state | Offline model | Ordered transitions, transcript binding, complaints, qualify/abort | Distributed agreement and public evidence |
| Multi-dealer DKG | Offline model | Common qualification, dual commitments, distributed shares, public key | Proven protocol, authenticated network, recovery |
| Threshold Schnorr/FROST | Educational model | Two rounds, one-time nonces, partial checks, ordinary final verification | RFC suite, isolated signers, durable nonce state, authenticated transport |
| Refresh, threshold BLS | No | Roadmap only | Future versions |
| Threshold HE and private ML | No | Research direction only | Separate reviewed design and libraries |

> The code is designed to make protocol ideas visible. It is not a production
> cryptographic implementation.
