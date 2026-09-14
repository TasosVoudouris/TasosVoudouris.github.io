# Original-to-reviewed file map

All substantive files from the supplied archive are accounted for below. IDE
metadata under `.idea/` was intentionally omitted.

| Original file | Reviewed location | Classification |
| --- | --- | --- |
| `digest.sage` | `src/foundations/digest.sage` | Hashing helper |
| `mathhelper.sage` | `src/foundations/math_helpers.sage` | Encoding/KDF/EC helpers |
| `rsa.sage` | `src/integer_factorization/rsa_keygen.sage` | RSA key generation |
| `paillier.sage` | `src/integer_factorization/paillier.sage` | Homomorphic encryption |
| `paillier_test.sage` | `examples/paillier_demo.sage`, `tests/run_all.sage` | Demo and assertions |
| `prime192v1.sage` | `src/elliptic_curves/curves/prime192v1.sage` | Legacy EC parameters |
| `ecc_param.sage` | `src/elliptic_curves/curve_generation.sage` | Educational parameter generation |
| `eckeygen.sage` | `src/elliptic_curves/key_generation.sage` | EC key generation |
| `ecdsa.sage` | `src/elliptic_curves/ecdsa.sage` | Digital signatures |
| `ectest.sage` | `examples/ecdsa_demo.sage` | ECDSA demonstration |
| `eckcdsa.sage` | `src/elliptic_curves/eckcdsa.sage` | EC-KCDSA signatures |
| `ecktest.sage` | `examples/eckcdsa_demo.sage` | EC-KCDSA demonstration |
| `ecies.sage` | `src/elliptic_curves/ecies.sage` | Hybrid EC encryption |
| `eciestest.sage` | `examples/ecies_demo.sage` | ECIES demonstration |
| `psec.sage` | `src/elliptic_curves/psec.sage` | PSEC-style EC encryption |
| `psectest.sage` | `examples/psec_demo.sage` | PSEC demonstration |
| `ECMQV.sage` | `src/key_agreement/ecmqv.sage`, `examples/ecmqv_demo.sage` | Authenticated key agreement study |
| `STS.sage` | `src/key_agreement/sts_key_confirmation.sage` | STS-inspired study |
| `ststest.sage` | `examples/sts_key_confirmation_demo.sage` | Handshake demonstration |
| `pairing.sage` | `src/pairings/miller_pairing_demo.sage` | Miller-function example |
| `rfc5091.sage` | `archive/incomplete/rfc5091_draft.sage.txt` | Incomplete preserved draft |
| Original `README.md` | `README.md` and `docs/` | Replaced by formal documentation |
