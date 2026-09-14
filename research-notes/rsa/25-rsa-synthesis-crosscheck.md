# RSA Synthesis — Editorial and Scientific Cross-Check

## Purpose

This is not another RSA cryptanalysis post.

It is the closure/index article for the RSA branch of the public CryptoCave site.

Its goals are:

1. organize the completed material by cryptographic layer;
2. show recurring mathematical dependencies;
3. distinguish primitive, scheme, implementation, and protocol failures;
4. define which RSA-related material is intentionally moved to later series;
5. provide a clean transition from content production to site organization.

---

## Mature source framing preserved

The mature CryptoBible RSA chapter summarizes RSA as:

```text
N = p*q
ed = 1 mod lambda(N)
m -> m^e mod N
```

while explicitly warning that the security lesson is broader than the arithmetic.

It identifies:

- textbook determinism and malleability;
- bad/reused parameters;
- small private exponents;
- Coppersmith-style small roots;
- ROCA / structured prime generation;
- padding/validity oracles;
- implementation leakage;
- quantum factoring.

This layer-based taxonomy is used as the backbone of the synthesis.

---

## Important scope boundary

The synthesis does NOT claim that every RSA-related subject has been published.

Instead it closes:

```text
RSA primitive
+ encryption
+ classical cryptanalysis
+ implementation-security branch
```

and deliberately moves:

```text
RSASSA-PSS / RSA signatures
    -> Digital Signatures

RSA-KEM / KEM-DEM
    -> Hybrid Encryption and KEMs

RSA certificates / PKI formats
    -> PKI and Certificates

full Shor derivation
    -> Quantum algorithms / cryptanalysis
```

This follows the mature manuscript's own canonical-home decision.

---

## Public post map

### Foundations reused by RSA

```text
01  Integers, Division, GCD
02  Extended Euclid / Bezout / modular inverse
03  Modular arithmetic
04  Multiplicative groups
08  Fast modular exponentiation / side channels
09  CRT RSA fault
10  Chinese Remainder Theorem
11  Primes / Miller-Rabin
12  RSA key generation
```

### RSA Deep Dives

```text
13  Textbook RSA failures
14  Common modulus
15  Hastad broadcast
16  Wiener
17  Coppersmith
18  Boneh-Durfee
19  Partial key exposure
20  Franklin-Reiter
21  Short-pad RSA
22  Bleichenbacher
23  Manger
24  ROCA
25  RSA synthesis
```

---

## Scientific distinctions retained

### Factoring versus RSA inversion

The synthesis does not state:

```text
RSA security = factoring.
```

It states only the durable direction:

```text
factoring N reveals the trapdoor.
```

The exact computational assumption must be named in a security proof.

### Mathematics versus implementation

CRT is explicitly presented as:

```text
correct theorem
+ useful optimization
```

whose two-branch implementation introduces a fault surface.

Likewise RSA exponentiation may be mathematically correct while execution
behavior leaks information.

### Coppersmith taxonomy

The article treats Coppersmith as a modelling language for:

```text
polynomial relation
+ bounded unknown
```

rather than as a generic "LLL breaks RSA" statement.

### Oracle taxonomy

Bleichenbacher and Manger are grouped under:

```text
decoder / validity information
```

rather than algebraic key-parameter failures.

### ROCA taxonomy

ROCA is grouped under:

```text
key-generation distribution
```

and not under generic factoring.

---

## Editorial goal for the site

This synthesis should become the natural hub for an RSA series page.

Recommended UI later:

```text
RSA Synthesis
    |
    +-- Foundations
    +-- Construction
    +-- Algebraic Cryptanalysis
    +-- Lattice / Small Roots
    +-- Oracle Cryptanalysis
    +-- Implementation Security
    +-- Key Generation
```

Each category can link to the relevant posts.

The included JSON manifest is intended as planning input for that later site
work; it is not required by the current Astro content schema.

---

## Publication checklist

Verify:

- Is the article shorter/lighter than a full deep dive?
- Does it explain why "RSA is broken" is an imprecise statement?
- Are attacks grouped by layer rather than chronology alone?
- Are all completed RSA deep dives linked?
- Are foundations visibly connected to later cryptanalysis?
- Is factoring not equated casually with RSA inversion?
- Are CRT's constructive and fault-surface roles both visible?
- Is Coppersmith treated as a general modelling language?
- Are Bleichenbacher and Manger clearly oracle-layer results?
- Is ROCA clearly a key-generation result?
- Are signatures/PSS intentionally deferred rather than accidentally omitted?
- Are RSA-KEM, PKI, and Shor given explicit future homes?
- Does the ending close RSA cleanly and transition to site organization?

Any "no" means another editorial pass.
