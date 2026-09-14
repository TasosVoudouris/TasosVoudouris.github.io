# Changelog

## Version 0.5.0

### Added

- `cryptocave_sss/frost.py`
- public FROST group information derived from Version 0.4 DKG outputs
- public participant verification shares derived from aggregate DKG commitments
- a custom, explicitly non-RFC-compatible teaching ciphersuite
- RFC-shaped domain-separated `H1`–`H5` roles
- fresh-randomness-plus-key-share nonce derivation
- two one-time nonce commitments per signer
- signer-local nonce storage, conservative deletion, and reuse rejection
- coordinator-side in-memory commitment tracking
- canonical ascending signing packages
- application envelope binding session, counter, purpose, DKG group, signer set,
  and payload
- optional application message-policy validation at each signer
- FROST binding factors, group commitment, Lagrange weights, and response shares
- individual response verification and identifiable local abort
- aggregate ordinary Schnorr signature generation and verification
- canonical public signing transcripts without private key/nonce fields
- six directly runnable FROST examples
- 44 FROST tests, bringing the complete suite to 141
- seven detailed CryptoCave chapters and an RFC conformance map

### Standards-aligned design decisions

- The commitment list encodes sorted `(identifier, D_i, E_i)` tuples.
- Binding factors include the group public key, message hash, commitment-list
  hash, and participant identifier as specified by RFC 9591's helper structure.
- The challenge signs `Serialize(R) || Serialize(Y) || msg`.
- Every signer uses its Lagrange coefficient at zero and deletes its nonce pair
  after one response.
- The coordinator validates every signature share before aggregation and verifies
  the ordinary final signature before returning it.
- DKG remains external to the signing core, and normal signing never
  reconstructs the group secret.

### Deliberately not claimed

- implementation of an RFC 9591 named ciphersuite or official test vectors;
- wire interoperability with maintained FROST implementations;
- meaningful security from the order-41 toy group;
- a production or formally proven DKG/FROST system;
- authenticated networking, separate trust domains, or durable nonce state;
- constant-time code, secure erasure, robustness, or post-quantum security;
- threshold encryption, homomorphic encryption, or private machine learning.

## Version 0.4.0

### Added

- `cryptocave_sss/dkg.py`
- one random dealer contribution per participant
- staged Pedersen qualification and Feldman-style public-key extraction
- fixed common qualified-dealer views
- configurable minimum-qualified-dealer policy
- aggregate secret/blinding key shares
- aggregate Pedersen and value commitment vectors
- public-key derivation without normal secret reconstruction
- canonical DKG transcripts and dealer records
- explicit DKG state and abort exceptions
- audit-only reconstruction and public-key equation check
- five directly runnable DKG examples
- 24 DKG tests and two Pedersen-extension tests
- five detailed CryptoCave DKG chapters

### Corrected during design

- The qualified set is fixed after the hidden Pedersen phase and before the
  value-commitment round.
- A later extraction failure does not silently remove a dealer and redefine the
  key. Version 0.4 aborts because the complete GJKR public-reconstruction
  recovery is not implemented.
- The public key is derived as a group product of qualified dealer constant
  value commitments; the group secret is not reconstructed by normal `run()`.
- Final participant key shares are verified under both aggregate commitment
  vectors.

### Deliberately not claimed

- a faithful or proven GJKR implementation;
- uniform adversarial output or selective-abort resistance;
- distributed broadcast, agreement, authentication, or private channels;
- production groups, encodings, side-channel protection, or secure erasure;
- refresh, FROST, threshold BLS, or threshold encryption.

## Version 0.3.0

### Added

- `cryptocave_sss/pedersen.py`
- Pedersen secret and blinding polynomials
- Hiding coefficient commitments and two-component private shares
- Pedersen verification reports and verified reconstruction
- Exhaustive hiding and tampering tests for the toy field
- A deliberate known-generator-relation binding counterexample
- `cryptocave_sss/vss_session.py`
- Canonical public session transcripts and SHA-256 identifiers
- An in-memory commitment-broadcast consistency model
- Participant verification states and complaint records
- Private dealer replacement responses
- Strict qualification and unresolved-complaint abort
- Six directly runnable examples
- Five detailed CryptoCave chapters
- Twenty-nine new tests, bringing the complete suite to 71

### Preserved

- All active Version 0.1 mathematical modules
- The Version 0.2 Feldman module, examples, tests, and documentation
- The sanitized legacy source selection and its warnings

### Deliberately not claimed

- Production Pedersen binding: the toy group is exhaustible and its generator
  relation is known.
- Real reliable broadcast: the board is one shared in-memory model.
- Message authentication: transcript hashes are unsigned identifiers.
- Publicly verifiable complaint evidence or malicious-participant blame.
- DKG, share refresh, FROST, threshold BLS, threshold encryption, or HE.

## Version 0.2.0

### Added

- `cryptocave_sss/feldman.py`
- Feldman public parameters and coefficient commitments
- Per-share verification results and aggregate reports
- Reconstruction from verified shares
- Strict abort policy when any supplied share is invalid
- Three directly runnable Feldman examples
- Fourteen Feldman-specific unit tests
- Four CryptoCave VSS chapters
- A security audit of the uploaded source archive

### Corrected from the uploaded experiments

- One polynomial is sampled for the entire distribution, not one polynomial per
  simulated participant or network request.
- Reconstruction uses exact Version 0.1 finite-field interpolation rather than
  symbolic floating-point evaluation.
- `threshold` means the number of shares required; degree is `threshold - 1`.
- Share labels are explicit and duplicate or unknown identifiers are rejected.
- Normal calls use operating-system randomness.
- Commitment and Shamir scalar moduli are required to match.
- Group parameters and commitment subgroup membership are validated.
- Participant signing keys are removed from the algebraic VSS layer because they
  were generated but unused.
- Failed verification produces an explicit report rather than continuing as if
  the share were valid.

### Deliberately deferred

- Pedersen VSS
- public verifiability with encrypted shares and zero-knowledge proofs
- KZG polynomial commitments
- reliable broadcast and complaints
- networking and MQTT
- DKG, refresh, FROST, threshold BLS, and threshold encryption

The original files are not silently rewritten. Selected source scripts are
preserved under `legacy/` with clear warnings, while credentials and unlicensed
bundled third-party material are excluded.
