# Ready material integration map

The material imported from `Ready.zip` is treated as finished or near-finished long-form source material. The integration policy is deliberately conservative: preserve the original explanations, derivations, examples, and implementation detail; correct only clear spelling/terminology/formatting problems during import; perform deeper scientific revisions later article-by-article when desired.

## Navigation rule

CryptoCave uses three separate axes:

- **Series** = intended reading order.
- **Topics** = broad subject classification; one article can belong to several topics.
- **Tags** = narrow concepts, algorithms, attacks, constructions, or implementation details.

The Ready material is not forced into the existing `Cryptography From Zero` sequence when it substantially overlaps with it. The newer beginner-first sequence remains intact, while the older detailed notes are exposed as deeper reference paths.

## Ordered series

### Start Here

1. **Cryptography Primer**
   - Introduction to Cybersecurity and Cryptography
   - Logical Operations and Base64 in Cryptography
   - Python and SageMath Cheat Sheet for Cryptography

2. **Cryptography From Zero**
   - Existing 00–12 sequence; retained as the main beginner-first path.

### Mathematical Foundations

3. **Number Theory & Algebra Reference**
   - Integers and divisibility
   - Modular arithmetic
   - Chinese Remainder Theorem
   - Groups and modular group structures
   - Euler’s totient and element orders
   - Prime numbers and factorization
   - Primality testing
   - Polynomial congruences and lifting
   - Strong pseudoprimes / Arnault fixed-base construction

### Core Cryptography

4. **Symmetric Cryptography & Hashing**
   - SPN block-cipher design
   - DES
   - AES-128
   - Padding and modes of operation
   - Hash functions

### Public-Key & Algebraic Systems

5. **Discrete Logarithm Algorithms**
   - DLP/ECDLP introduction
   - Baby-step giant-step
   - Pohlig–Hellman
   - Pollard’s rho for ECDLP

6. **Diffie–Hellman & ElGamal**
   - Diffie–Hellman key exchange
   - Safe primes and subgroup structure
   - Diffie–Hellman failure modes and active attacks
   - ElGamal encryption

7. **Elliptic Curves**
   - Group law and Weierstrass curves
   - Curves over finite fields
   - Models, j-invariant, and torsion
   - Edwards and twisted Edwards curves
   - Pairings
   - Schoof point counting
   - Singular-curve DLP reduction
   - MOV attack
   - Smart attack on anomalous curves
   - Isogeny paths and CM-related arithmetic

### Security Analysis

8. **RSA Deep Dives**
   - Existing 13–25 sequence from textbook RSA failures through ROCA and synthesis.

## Standalone topic articles

These are indexed through Topics and Tags rather than padded into artificial one-article series:

- The Paillier Cryptosystem
- The RSA Cryptosystem: Extended Reference
- Robust Secret Sharing via Gao Decoding

## Source-code policy

Ready implementations are retained under:

```text
experiments/ready-material/
```

Where a matching implementation exists, the article frontmatter contains `sourcePath`, and the article header links directly to the corresponding GitHub directory.

## Figures

Recovered local figures are normalized into:

```text
public/images/ready/<article-slug>/
```

This avoids the original Windows-only case-insensitive path assumptions and makes GitHub Pages image resolution deterministic.
