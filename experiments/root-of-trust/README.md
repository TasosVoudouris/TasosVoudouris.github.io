# Root of Trust: companion code

Code for the article series at https://tasosvoudouris.github.io/root/ .
Teaching models only: never use them to protect anything real.

| File | Article | Run |
|---|---|---|
| `00_toy_chain.py` | Part 00, "Who do you trust?" | `python 00_toy_chain.py` |
| `test_00_toy_chain.py` | checks the six verdicts the article quotes | `python -m unittest test_00_toy_chain` |
| `der.py` | Part 01, a DER encoder and strict decoder from scratch | imported by `01_certificate.py` |
| `01_certificate.py` | Part 01, "A certificate, byte by byte" | `python 01_certificate.py --write` |
| `test_01_certificate.py` | checks the encoder and every offset and size Part 01 quotes | `python -m unittest test_01_certificate` |
| `02_handshake.py` | Part 02, "The handshake bill": three chains with real SCTs, live TLS 1.3 handshakes | `python 02_handshake.py` |
| `test_02_handshake.py` | checks every size Part 02 quotes; live checks need OpenSSL 3.5+ | `python -m unittest test_02_handshake` |
| `03_ct_toy.py` | Part 03, "When authorities lie": a toy CT ecosystem replaying real attacks, nine verdicts | `python 03_ct_toy.py` |
| `test_03_ct_toy.py` | checks the nine verdicts | `python -m unittest test_03_ct_toy` |
| `04_merkle.py` | Part 04, "Merkle trees from zero": RFC 6962 tree, proofs, RFC 9162 verifiers, attacks | `python 04_merkle.py` |
| `test_04_merkle.py` | test vectors, RFC examples, exhaustive proof checks | `python -m unittest test_04_merkle` |
| `05_witness.py` | Part 05, "Notes, checkpoints, witnesses": C2SP signed notes, checkpoints, cosignatures, a witness, split views, quorums | `python 05_witness.py` |
| `test_05_witness.py` | the signed-note spec's test vector, witness status codes, scenarios, the quorum rule | `python -m unittest test_05_witness` |
| `06_quantum_bill.py` | Part 06, "The quantum bill": every scheme measured, the bill by role, the cheapest mixes | `python 06_quantum_bill.py` (optional: `pip install liboqs-python`) |
| `test_06_quantum_bill.py` | the model reproduces Part 02; the optimizer's answers | `python -m unittest test_06_quantum_bill` |
| `07_mtc.py` | Part 07, "Merkle Tree Certificates": a toy MTC CA from draft -07, standalone and landmark-relative certificates, a relying party, the bill | `python 07_mtc.py` |
| `test_07_mtc.py` | the draft's encoding example and Appendix C vectors, issuance, both certificate kinds, rejections, sizes | `python -m unittest test_07_mtc` |
| `08_landmarks.py` | Part 08, "Landmarks you can check": subtree consistency proofs, cosigned checkpoints, a week of landmarks, the update service, stale clients | `python 08_landmarks.py` |
| `test_08_landmarks.py` | the draft's examples and Appendix C vectors, exhaustive proof checks, landmark validation and attacks, the staleness model | `python -m unittest test_08_landmarks` |
| `09_tiles.py` | Part 09, "Tiled logs": a C2SP tlog-tiles writer and client, the spec's examples, proofs from tiles alone, tampering, caching, monitor bandwidth | `python 09_tiles.py` (add `--write DIR` to browse the files) |
| `test_09_tiles.py` | paths and layout against the spec, immutability, proofs equal to Parts 04 and 08, tampering, monitor cost | `python -m unittest test_09_tiles` |
| `10_never_fork.py` | Part 10, "A log that never forks": five commit protocols for a tiled log, crashed at every step, rolled back, twinned, and judged | `python 10_never_fork.py` |
| `test_10_never_fork.py` | which protocols fork, which get stuck, conditional writes, staging, rollback, twins, a reused key | `python -m unittest test_10_never_fork` |
| `11_vectors.py` | Part 11, "From toy to QCERT": freezes Parts 04 to 09 into `vectors/root-of-trust-vectors.json` | `python 11_vectors.py` (or `--check`) |
| `test_11_vectors.py` | the vector file is reproducible and verifies with the Python reference | `python -m unittest test_11_vectors` |
| `rust/` | the Merkle, subtree, tile and MTC core in Rust, tested against the same vectors | `cd rust` then `cargo test` |
| `01_example_*.der` | the certificates Part 01 dissects (leaf, ML-DSA-44 leaf, toy CA) | `openssl asn1parse -inform DER -in 01_example_ed25519.der -i` |

Needs Python 3.10+ and `pip install cryptography` (version 46 or newer for the ML-DSA part of Part 01).
