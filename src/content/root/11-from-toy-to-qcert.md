---
title: 'From toy to QCERT'
description: 'The end of the series and the start of the implementation. Every experiment mapped to the module it becomes; one deterministic file of test vectors frozen from the Python reference; a Rust crate of about 800 lines that passes all of them, recomputes the draft Appendix C hashes, and verifies a landmark-relative certificate end to end; the test that caught my own wrong assumption; and what a real system still needs.'
part: 11
pubDate: 2026-11-24
tags:
  - merkle-tree-certificates
  - rust
  - test-vectors
  - post-quantum
  - qcert
companion: experiments/root-of-trust
---

Ten parts built the whole stack in Python, from the bytes of an X.509 certificate to a crash-safe tiled log of Merkle Tree Certificates. The Python was written to be read: short functions, one idea each, a printout for every claim. That makes it a good **reference**, but not an implementation. A real MTC CA, witness or relying party needs a language with a type system and predictable performance, and code that a security review can trust.

This last part builds the bridge. It does three things:

1. It maps every experiment to the module it becomes, and states what does **not** become code.
2. It freezes what the Python computes into one file of **test vectors**, so that any other implementation can be checked against exactly the same bytes.
3. It ports the hashing and parsing core to **Rust**, in a small crate called `rot-mtc`, and runs it against those vectors, including the draft's own Appendix C hashes and a complete landmark-relative certificate from Part 07.

This is also the starting point of my implementation work in the **QCERT** project, which works on post-quantum TLS and Merkle Tree Certificates. The crate here is not that implementation. It is the tested core and the method, published so that the method can be checked.

By the end you should be able to:

1. say which part of the series becomes which module, and why some parts become rules instead;
2. explain what makes a good test vector file, and why it must be deterministic;
3. read the Rust port of each algorithm and recognise the Python it came from;
4. follow the verification of a landmark-relative certificate in Rust, step by step;
5. list what a real system still needs, in a sensible order.

The new code is `experiments/root-of-trust/11_vectors.py`, `test_11_vectors.py`, and the Rust crate in [`experiments/root-of-trust/rust`](https://github.com/TasosVoudouris/TasosVoudouris.github.io/tree/main/experiments/root-of-trust).

## The map

<img src="/images/root/11-map.svg" alt="Python experiments on the left, Rust modules on the right: der.py and Part 01 to der.rs, 04_merkle.py to merkle.rs, 05_witness.py to note.rs, 07_mtc.py to mtc.rs and subtree.rs, 08_landmarks.py to subtree.rs, 09_tiles.py to tiles.rs. 10_never_fork.py becomes a rule for the log writer. Parts 00, 02, 03 and 06 explain the problem and do not become code." width="1000" height="640" loading="lazy" />

| part | Python | becomes | why |
|---|---|---|---|
| 00, 02, 03, 06 | toy chain, handshake, CT toy, quantum bill | nothing | they explain and measure the problem |
| 01 | `der.py`, `01_certificate.py` | `der.rs` | just enough DER to take a certificate apart |
| 04 | `04_merkle.py` | `merkle.rs` | RFC 9162 tree hash, inclusion and consistency proofs |
| 05 | `05_witness.py` | `note.rs` | checkpoint bodies and signed-note key IDs |
| 07 | `07_mtc.py` | `mtc.rs`, `subtree.rs` | encodings, covering subtrees, the relying party check |
| 08 | `08_landmarks.py` | `subtree.rs` | subtree consistency proofs |
| 09 | `09_tiles.py` | `tiles.rs` | tlog-tiles paths and layout |
| 10 | `10_never_fork.py` | a rule | stage, lock, then publish: a property of the log writer |

Two rows deserve a comment. Parts 00, 02, 03 and 06 never become code because they are arguments, not mechanisms. They establish why the design exists: certificates are chains of signatures, signatures dominate the handshake, transparency needs logs, and post-quantum signatures make all of it expensive. Part 10 does not become a module because its result is a rule about **order**. The log writer must stage its tiles, commit to a lock with compare-and-swap, and only then publish. That rule will be enforced by the structure of the writer, and tested by injecting faults, as Part 10 did.

## Test vectors: one set of bytes, two languages

<img src="/images/root/11-pipeline.svg" alt="The Python reference computes everything; 11_vectors.py freezes the results into root-of-trust-vectors.json, deterministic, about 349 KB; the Rust crate reads the same file in cargo test. The draft Appendix C hashes are recomputed on both sides." width="1000" height="460" loading="lazy" />

A port is only as good as the evidence that it computes the same thing as the original. Reading two programs side by side is not evidence. Comparing outputs is. So the first step is to freeze the outputs:

```text
wrote vectors/root-of-trust-vectors.json (348,850 bytes)
    21 tree hashes
   210 inclusion proofs
   210 consistency proofs
   567 subtree consistency proofs
    10 covering cases
    14 tile paths
  a landmark-relative certificate of 1,855 bytes, entry 1005, subtree [0, 1024), 10 proof hashes
  draft Appendix C hashes: C.1.1, C.1.2, C.1.3, C.1.4
```

<img src="/images/root/11-vectors.svg" alt="What the vector file holds: 420 Merkle proofs, 567 subtree consistency proofs, 21 subtree validity and covering cases, 23 tile cases, 10 MTC encodings including a certificate, and 4 Appendix C hashes that each stand for thousands of proofs." width="1000" height="480" loading="lazy" />

Four rules shaped the file:

- **Deterministic.** Every value comes from fixed inputs: leaves that are the single bytes 0, 1, 2 and so on, keys derived from fixed labels, a fixed date. ML-DSA signatures are randomized, so the file contains none; the landmark-relative certificate has no signatures by design. `python 11_vectors.py --check` regenerates the file in memory and compares it byte for byte, and the tests do the same.
- **Exhaustive where it is cheap.** Every inclusion and consistency proof for every tree up to 20 leaves, and every valid subtree consistency proof in those trees. Small trees cover every shape the recursion can take: powers of two, one past a power of two, unbalanced right edges.
- **Edges where it is not.** Subtree validity and covering at 2<sup>47</sup>, 2<sup>48</sup>, 2<sup>63</sup> and 2<sup>64</sup> − 1, from the draft's Appendix C.2, and tile paths with eight forbidden spellings.
- **Anchored outside.** The four Appendix C.1 hashes are not my outputs. They are the draft's, and both implementations must recompute them from scratch. That keeps the Python and the Rust from agreeing with each other on a shared mistake.

The format is plain JSON with hex strings and integers. Indexes up to 2<sup>64</sup> − 1 are written as exact integers, which Python and Rust's `serde_json` both read without loss. A JavaScript implementation would need care there, because its numbers are 64-bit floats.

## The Rust crate

The crate `rot-mtc` has six modules and about 800 lines, plus about 240 lines of tests. Its only dependency is the `sha2` crate for SHA-256. The tests also use `serde_json` and `hex`. It needs Rust 1.87 or newer.

The port is deliberately literal. Each function has the same name and the same recursion as its Python original, with comments pointing back. A few things changed because Rust makes them explicit:

**Types say what a value is.** A hash is `[u8; 32]`, not "some bytes". Positions in a log are `u64`, which matches the draft's limit of 2<sup>48</sup> − 1 entries per log and still holds the larger values that subtree arithmetic touches. Arithmetic that could overflow is written so it cannot. `bit_ceil` returns `None` when the next power of two would be 2<sup>64</sup>, and `valid_subtree` handles that case explicitly instead of wrapping around:

```rust
pub fn valid_subtree(start: u64, end: u64) -> bool {
    if start > end {
        return false;
    }
    match bit_ceil(end - start) {
        Some(c) => start.is_multiple_of(c),
        None => start == 0, // BIT_CEIL = 2^64: only a start of 0 is a multiple
    }
}
```

**Bit tricks become explicit.** Python found "the most significant bit where start and last differ" with `bit_length`. Rust uses `leading_zeros`, and the covering algorithm of §4.5.1 reads almost line for line:

```rust
let last = end - 1;
let split_bit = 63 - (start ^ last).leading_zeros();          // most significant differing bit
let mid = last & !((1u64 << split_bit) - 1);
let low = start & ((1u64 << split_bit) - 1);
let zeros = !low & ((1u64 << split_bit) - 1);                  // zero bits of start below split
let left_split = if zeros == 0 { 0 } else { 64 - zeros.leading_zeros() };
let left_start = if left_split == 0 { start } else { start & !((1u64 << left_split) - 1) };
((left_start, mid), (mid, end))
```

**Parsers are strict and return errors.** `der::read` rejects indefinite lengths, non-minimal lengths and values that run past the buffer. `MtcProof::parse` rejects trailing bytes, partial hashes, empty cosigner IDs, and cosignatures that are unsorted or repeated. `tiles::parse_tile_path` rejects every spelling the spec forbids. Errors are plain strings here; a production crate would use an error type.

**No signatures.** The crate hashes and parses, nothing else. Signatures will come from a vetted library, never from code written for a blog. The crate's scope is exactly the part where this series found its bugs: lengths, indexes, orders and bit operations.

## What the tests caught

```text
test checkpoint_body_and_key_id ... ok
test landmark_relative_certificate_end_to_end ... ok
test merkle_tree_hashes_and_proofs ... ok
test mtc_encodings ... ok
test subtree_consistency_proofs ... ok
test subtree_validity_and_covering ... ok
test tile_paths_and_layout ... ok
test draft_appendix_c ... ok
test result: ok. 8 passed; 0 failed
```

That is the final state. The first run was not clean. In the Merkle test I had added what looked like an obvious negative check: an inclusion proof for a tree of n leaves should fail if the verifier is told the tree has n + 1 leaves. The test failed, but the code was fine. The check was wrong. Across all 210 inclusion proofs in the file, **154 still verify when the size is off by one**, because the shape of the path, and therefore the verification loop, is the same for both sizes.

That is Part 04's lesson, back again: an inclusion proof does not bind the tree size. In RFC 9162 the size comes from the signed tree head, and in MTC from the cosigned `[start, end)` inside the subtree message (Part 07), which is why the draft puts the range in the signed bytes. My test now asserts what is actually true (a proof cannot verify for an index outside the tree) and carries a comment explaining what it does not assert. Writing it down this way is the point of the exercise: a port is where the assumptions of the original get tested a second time.

The Appendix C test is the strongest one. The Rust code regenerates all four of the draft's running hashes: every valid subtree hash, every subtree inclusion proof, every subtree consistency proof for trees up to 130 entries, and every covering pair, tens of thousands of lines. The four final hashes are identical to the draft's. With optimisation on for tests, the whole suite runs in about a second.

## A certificate, end to end

<img src="/images/root/11-verify.svg" alt="Seven steps of verify_landmark_relative: split the DER; check both algorithm fields are id-alg-mtcProof; split the serial into log 1 and index 1005; parse the MTCProof, subtree [0, 1024), 10 hashes, 0 signatures; rebuild the log entry, the same bytes as Python; hash it and evaluate the proof; compare with the trusted landmark hash." width="1000" height="620" loading="lazy" />

The last test brings the series together. Its input is the 1,855-byte landmark-relative certificate from Part 07, exactly as the Python CA built it, plus one trusted landmark subtree hash, as Part 08's update service would have delivered it. `verify_landmark_relative` follows §7.2:

1. split the certificate into TBSCertificate, signatureAlgorithm and signatureValue;
2. check that both algorithm fields are id-alg-mtcProof (1.3.6.1.5.5.7.6.67, parameters absent);
3. split the serial into log number 1 and index 1,005;
4. parse the MTCProof out of the BIT STRING: subtree `[0, 1024)`, ten proof hashes, no signatures;
5. **rebuild the MTCLogEntry** from the TBSCertificate: copy version, issuer, validity, subject and extensions; replace the SubjectPublicKeyInfo by its algorithm and its SHA-256; prefix the four bytes `00 00 00 01`;
6. hash it as a leaf and evaluate the inclusion proof;
7. compare the result with the trusted landmark hash.

The test checks that the rebuilt entry is **byte for byte** the one the Python CA put in its log, and that verification returns log 1, index 1,005, subtree `[0, 1024)`. Then it tries three failures. A wrong landmark hash is rejected; a missing landmark is rejected with "cosignatures would be needed"; and changing one letter of the subject name, `site5.example` to `site6.example`, is rejected because the rebuilt entry, and so the leaf, and so the evaluated hash, no longer match.

Notice what this verification does **not** contain: no signature check, no public key operation, nothing post-quantum. A chain of SHA-256 hashes connects the certificate to a hash the browser already holds. That is the result Part 07 priced at 4,296 bytes of handshake authentication against 15,271, and now it runs in a compiled language against frozen bytes.

## What a real system still needs

<img src="/images/root/11-next.svg" alt="Done: hashing, proofs, tiles, encodings, landmark check. Next, in order: signatures through a vetted ML-DSA library; cosigners for subtrees and checkpoints, with witnesses; the log writer with tiles, lock and staging from Part 10; landmarks, allocation, validation and distribution from Part 08. Later: TLS trust anchor IDs and certificate selection. Always: fuzz every parser." width="1000" height="560" loading="lazy" />

The crate is the core, not the system. In the order I would build the rest:

1. **Signatures.** ML-DSA for cosigners and for the CA's cosigner, Ed25519 where the C2SP formats use it, all from vetted libraries, behind one small interface so the scheme can change. Part 07 showed that the cosignatures are most of a standalone certificate's size, so that interface should not assume any particular signature length.
2. **Cosigning.** CosignedSubtree messages for certificates and checkpoints, a witness that keeps its last cosigned checkpoint and checks consistency before signing again (Part 05), and the relying-party policy of §7.3.
3. **The log writer.** Part 09's tiles, written with Part 10's order: stage, compare-and-swap a lock, copy, publish. Plus fault injection tests that crash it at every step, as Part 10 did, against real storage.
4. **Landmarks.** Allocation with expirations, bundles for the update service, and validation of reference checkpoints and subtree consistency proofs before anything is trusted (Part 08).
5. **TLS.** Trust anchor IDs, landmark groups, and choosing between the standalone and the landmark-relative certificate (§8).

And throughout: **fuzz every parser.** DER, MTCProof, tile paths and signed notes all read bytes that an attacker controls. The vector file says what must be accepted. A fuzzer finds what must not be.

Each of these steps should start the way this part did: new vectors from a reference first, then the code. The draft will keep changing; when it does, the vectors are where the change shows up first.

## The series, in one table

| part | question | answer, in one line |
|---|---|---|
| 00 | who do you trust? | a root you never verify, and a chain of signatures from it |
| 01 | what is a certificate? | DER bytes you can read by hand |
| 02 | what does it cost? | the certificate chain dominates the TLS handshake |
| 03 | what if a CA lies? | logs make issuance public: Certificate Transparency |
| 04 | how do logs prove things? | Merkle trees: inclusion and consistency proofs |
| 05 | who checks the logs? | witnesses cosign checkpoints, so a log cannot show two views |
| 06 | what do post-quantum signatures do to this? | five signatures and two keys: the bill multiplies |
| 07 | can we remove signatures? | Merkle Tree Certificates: 4,296 bytes against 15,271, with landmarks |
| 08 | why trust a landmark? | subtree consistency proofs against cosigned checkpoints |
| 09 | how is a log served? | static, cacheable tiles: 98.9 percent cache hit rate |
| 10 | how does a log never fork? | a compare-and-swap lock, and staging before publishing |
| 11 | how does it become software? | frozen vectors, a strict port, and tests that catch assumptions |

## Try it

From the `experiments\root-of-trust` folder:

```text
python 11_vectors.py --check
python -m unittest test_11_vectors
cd rust
cargo test
```

The first command should print `identical to a fresh run`. The last needs Rust 1.87 or newer (`rustup update` if not); the first build downloads three small crates.

To run every Python test of the series at once:

```text
python -m unittest discover -p "test_*.py"
```

Exercises:

1. Add a Rust function `tiles::layout_to_paths(size)` that lists every file of a tiled log, and test it against Part 09's `--write` output.
2. Port Part 09's `range_hash` to Rust as a trait with a `node(level, index)` method, and implement it once over a slice and once over a map of tiles.
3. Add a vector for a **standalone** certificate without its signatures, and teach `verify_landmark_relative` to return the CosignedSubtree message that a cosigner would have to have signed.
4. Write a fuzz target for `MtcProof::parse` with `cargo fuzz`. What should hold for every input that parses? (Hint: `encode(parse(b)) == b` when the cosignatures are already sorted.)
5. Make the vector file smaller without losing coverage: which sections could become running hashes, the way Appendix C does it?
6. Port Part 08's landmark validation. Which new vectors do you need first?

## Reader checkpoint

<details>
<summary><strong>1.</strong> Why must the vector file be deterministic, and what had to be left out to make it so?</summary>

So that regenerating it gives the same bytes, and any difference means a real change. ML-DSA signatures are randomized, so no signature is included; the landmark-relative certificate has none by design.

</details>

<details>
<summary><strong>2.</strong> Why include the draft's Appendix C hashes when the file already has hundreds of proofs from the Python reference?</summary>

The Python proofs only show that Rust agrees with Python. Appendix C comes from the draft's authors, so recomputing it on both sides catches a mistake that Python and Rust might share.

</details>

<details>
<summary><strong>3.</strong> An inclusion proof for a tree of n leaves verifies with size n + 1 in 154 of 210 cases. Is that a bug?</summary>

No. The verification loop depends only on the shape of the path, which is often the same for both sizes. The size must come from something signed: the checkpoint in RFC 9162, the cosigned subtree range in MTC.

</details>

<details>
<summary><strong>4.</strong> What does verifying a landmark-relative certificate cost in public-key operations?</summary>

None. The relying party rebuilds the log entry, hashes it, evaluates the inclusion proof and compares the result with a landmark hash it already trusts.

</details>

<details>
<summary><strong>5.</strong> Why does Part 10 become a rule instead of a module?</summary>

Its result is about the order of writes (stage, lock, copy, publish), which is a property of how the log writer is structured, enforced by its design and tested by fault injection, not a function that can be called.

</details>

## Thank you for reading

This series started with the question every TLS connection answers without asking: who do you trust? It ends with an answer that trusts less: a CA whose every issuance is public before it is usable, witnesses that hold it to one history, and certificates whose proof is a handful of hashes instead of a stack of post-quantum signatures. The draft is not finished, and neither is the work. But every claim in these twelve parts can be checked: the code runs, the vectors are frozen, and the references point to the standards that make them true.

## References

- D. Benjamin, D. O'Brien, B. E. Westerbaan, L. Valenta and F. Valsorda, [*Merkle Tree Certificates*](https://www.ietf.org/archive/id/draft-ietf-plants-merkle-tree-certs-07.html), draft-ietf-plants-merkle-tree-certs-07, October 2026: §4 (subtrees), §5.2 (log entries), §6.1 (MTCProof), §7.2 (verification), Appendix C (test vectors).
- B. Laurie, E. Messeri and R. Stradling, RFC 9162, *Certificate Transparency Version 2.0*, 2021: tree hashes and proof verification.
- C2SP, [*tlog-tiles*](https://github.com/C2SP/C2SP/blob/main/tlog-tiles.md), [*tlog-checkpoint*](https://c2sp.org/tlog-checkpoint) and [*signed-note*](https://c2sp.org/signed-note).
- RustCrypto, [*sha2*](https://crates.io/crates/sha2): the one dependency of the crate.
