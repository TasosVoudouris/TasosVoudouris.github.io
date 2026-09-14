# Primary References

The chapters cite these sources by short name. Standards and original papers are preferred to secondary explanations.

## Standards and specifications

- **FIPS 180-4 — Secure Hash Standard.** SHA-1 and the SHA-2 family, including padding, constants, and algorithms. [NIST publication page](https://csrc.nist.gov/pubs/fips/180-4/upd1/final)
- **FIPS 202 — SHA-3 Standard.** SHA3-224/256/384/512, SHAKE128/256, and Keccak-p permutations. [NIST publication page](https://csrc.nist.gov/pubs/fips/202/final)
- **NIST SP 800-185.** cSHAKE, KMAC, TupleHash, and ParallelHash. [NIST publication page](https://csrc.nist.gov/pubs/sp/800/185/final)
- **FIPS 198-1 — HMAC.** The NIST HMAC specification. NIST announced in 2025 that it planned to withdraw this FIPS after moving updated material to SP 800-224; the linked page records the current status. [NIST publication page](https://csrc.nist.gov/pubs/fips/198-1/final)
- **RFC 2104 — HMAC.** The original IETF HMAC construction. [RFC Editor](https://www.rfc-editor.org/info/rfc2104)
- **RFC 5869 — HKDF.** Extract-and-expand key derivation based on HMAC; useful for understanding why a KDF and a MAC have different interfaces even when both use HMAC internally. [RFC Editor](https://www.rfc-editor.org/info/rfc5869)
- **RFC 7693 — BLAKE2.** BLAKE2b/BLAKE2s, including the optional keyed mode. [RFC Editor](https://www.rfc-editor.org/info/rfc7693)
- **NIST SP 800-63B-4.** Current NIST guidance on password verifier storage, including salts, schemes, and cost factors. [NIST publication page](https://csrc.nist.gov/pubs/sp/800/63/b/4/final)

## Foundations and cryptanalysis

- Ralph Merkle, *Secrecy, Authentication, and Public Key Systems* (1979), and Ivan Damgård, *A Design Principle for Hash Functions* (CRYPTO 1989), introduced the paradigm now called Merkle–Damgård.
- John Black, Phillip Rogaway, and Thomas Shrimpton, *Black-Box Analysis of the Block-Cipher-Based Hash-Function Constructions from PGV* (CRYPTO 2002), systematized one-block-length block-cipher compression modes.
- Antoine Joux, *Multicollisions in Iterated Hash Functions* (CRYPTO 2004), showed that finding multicollisions in an iterated hash is much cheaper than a naive random-function model suggests. [IACR record](https://www.iacr.org/archive/crypto2004/31520306/multicollisions.pdf)
- Marc Stevens et al., *The First Collision for Full SHA-1* (CRYPTO 2017), reported the SHAttered collision. [Paper](https://shattered.io/static/shattered.pdf)
- Gaëtan Leurent and Thomas Peyrin, *SHA-1 is a Shambles* (2020), reported a practical chosen-prefix collision and a PGP application. [IACR ePrint 2020/014](https://eprint.iacr.org/2020/014)
- Mihir Bellare, Ran Canetti, and Hugo Krawczyk, *Keying Hash Functions for Message Authentication* (CRYPTO 1996), introduced and analyzed NMAC/HMAC. [UCSD paper copy](https://cseweb.ucsd.edu/~mihir/papers/kmd5.pdf)
- Lorenzo Grassi et al., *Horst Meets Fluid-SPN: Griffin for Zero-Knowledge Applications* (CRYPTO 2023; first posted 2022). [IACR ePrint 2022/403](https://eprint.iacr.org/2022/403)

## Status cautions

- SHA-1 appears in FIPS 180-4 because that document specifies its algorithm; this is not a recommendation to start new SHA-1 deployments. Transition rules are application-specific and change over time. Consult the current NIST transition guidance and the protocol standard governing the system.
- FIPS 202 and SP 800-185 were under NIST review when this module was revised. Parameter tables here reproduce the published standards, not proposed revisions.
- Algebraic hashes such as Griffin are protocol components with exact field and parameter requirements. They are not drop-in replacements for SHA-256 or SHA3-256 in ordinary applications.
