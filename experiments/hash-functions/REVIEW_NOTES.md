# Editorial and Technical Review Notes

This file records substantive changes made while converting the supplied `Hash&Macs` archive into a publishable CryptoCave module.

## Corrected technical issues

1. **Birthday collision search.** The original code generated two fresh inputs and compared only that pair. That strategy succeeds with probability (2^{-n}) per pair and therefore takes about (2^n) work. The corrected lab retains every digest already seen, which is the table-based birthday attack with time and memory near (2^{n/2}).
2. **Birthday constants.** At (q=\sqrt{N}), the approximate collision probability is (1-e^{-1/2}\approx39.3\%\), not (50\%\). A (50\%\) chance occurs near (\sqrt{2N\ln 2}\approx1.1774\sqrt N); the expected stopping time is about (\sqrt{\pi N/2}\).
3. **Bit truncation.** Converting a hexadecimal digest to a binary string had removed leading zeroes. The new code converts all 256 bits to an integer and then right-shifts, so the selected field always has the declared width.
4. **Password guidance.** HMAC is a MAC, not a password-storage scheme. The revised text explains salts, cost parameters, offline guessing, and dedicated password hashing.
5. **Merkle–Damgård padding.** The final length field encodes the original message length in bits. It is part of MD strengthening and collision-resistance reasoning; it does **not** prevent length extension.
6. **SHA-256 implementation.** Duplicate functions, integer/byte length ambiguity, accidental leading-zero loss, and hand-adjusted padding were removed. The replacement matches `hashlib.sha256` at empty, standard, and block-boundary test vectors.
7. **Length extension.** The former demonstration manually added `512` to an integer representation and mixed SHA-1 and SHA-256 descriptions. The new lab computes exact glue padding, resumes from the digest state, models an unknown secret-length guess, verifies the forged message, and shows that the same method fails against HMAC.
8. **SHA-3 parameters.** The old `SHA3_256` class used a 512-bit rate; FIPS 202 SHA3-256 uses (r=1088) and (c=512). Its byte order, suffix, padding, absorption, squeezing, and output extraction were also inconsistent. The replacement matches Python's FIPS 202 implementation across rate boundaries and for multi-block SHAKE output.
9. **Keccak terminology.** Keccak, SHA-3, and SHAKE are no longer treated as interchangeable. The revised text identifies their different domain-separation suffixes and output rules.
10. **MAC security.** The chapter now uses an explicit chosen-message forgery experiment, separates EUF-CMA from strong unforgeability, and explains tag truncation, verification attempts, replay, canonical encoding, key separation, and constant-time comparison.
11. **CBC-MAC.** Its security claim is restricted to fixed-length messages under the standard assumptions. Variable-length use is not presented as safe; CMAC or a standardized alternative is recommended.
12. **SHA-1 collision.** Generated Sage wrappers were removed. The historical blocks now run with the Python standard library and assert different messages, equal SHA-1 digests, and unequal SHA-256 digests.
13. **Griffin.** The Sage lab no longer mutates its caller's input list, uses the standard-library SHAKE256 interface for deterministic constants, checks output length, and prints deterministic regression examples rather than random values.

## Structural cleanup

- Repeated introductions and pasted conversational phrases were removed.
- Chapters were ordered by dependency and assigned stable, relative GitHub links.
- Executable code was separated from Markdown so snippets do not silently diverge from tested files.
- The duplicated `CompactFIPS202.py`, generated `.sage.py` files, `__pycache__`, empty folders, and notebook output were not carried forward. Their educational content is superseded by the tested SHA-3 and SHA-256 modules.
- Eleven supplied diagrams were normalized to lower-case `.png` paths and retained with their relevant chapters. A later design pass can replace them without changing the chapter structure.

## Source-archive handling

Four PDF files in the source archive were reviewed as background but not republished:

- `Hashes (keyless).pdf` — basic personal notes, superseded by Chapters 1–3.
- `Message Authentication Code.pdf` — basic personal notes, superseded by Chapter 6.
- `Hashing Showdown: SHA-2 vs Keccak vs Poseidon` — a saved third-party Medium article with unclear redistribution permission.
- `Securing Your Messages: ... ElGamal ... Cramer-Shoup ... ECIES` — a saved third-party article outside this module's scope.

Excluding these copies avoids publishing off-topic material or material without an established repository-compatible license. The primary standards and research papers used by the rewritten chapters are linked in [REFERENCES.md](REFERENCES.md).
