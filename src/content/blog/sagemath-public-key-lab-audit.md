---
title: "SageMath Public-Key Cryptography Lab: Auditing RSA/CRT, Diffie–Hellman, ElGamal, ECDH, and Textbook Signatures"
description: "A cleaned audit of recovered SageMath public-key exercises, preserving the useful algebra while correcting parameter generation, protocol labels, security claims, and textbook-signature pitfalls."
pubDate: "2017-01-30"
updatedDate: "2026-09-14"
topics:
- "Public-Key Cryptography"
- "Key Exchange"
- "Digital Signatures"
- "Cryptanalysis"
- "Cryptographic Engineering"
tags:
- "sagemath"
- "rsa"
- "crt"
- "common-modulus"
- "diffie-hellman"
- "elgamal"
- "ecdh"
- "textbook-rsa"
- "code-audit"
difficulty: "Intermediate"
status: "Validated"
sourcePath: "experiments/sagemath-public-key-lab"
draft: false
---
A second recovered SageMath workbook moves from classical ciphers into RSA, CRT, Diffie–Hellman, ElGamal, ECDH, discrete logarithms, elliptic-curve ElGamal, and textbook RSA signatures.

The workbook is useful, but it was written as coursework rather than as a reusable cryptographic library. Some examples are correct mathematical toys. Some functions ignore their own parameters. One "ElGamal" exercise is actually a DH-derived multiplicative mask. And several examples would be dangerous if copied into real code without understanding their security model.

This article keeps the useful algebra and audits the rest.

![Audit map for the recovered public-key SageMath workbook](/images/blog/sagemath/public-key-lab-audit.svg)

## 1. RSA key generation: the first hidden bug

The old function roughly does:

```python
p = next_prime(ZZ.random_element(2^(bits//2 + 1)))
q = next_prime(ZZ.random_element(2^(bits//2 + 1)))
```

This does **not** guarantee that $p$ and $q$ have the requested half-size.

Sampling uniformly below an upper bound can produce values with substantially fewer bits. Therefore a call such as

```python
keygen(1024)
```

does not necessarily yield a 1024-bit modulus.

A proper toy generator should sample in an interval such as

$$
2^{k-1}\le p<2^k
$$

for the intended prime size $k$, and should ensure

$$
p\ne q.
$$

Production RSA key generation has many additional requirements and should use a vetted library, not a worksheet prime loop.

## 2. RSA arithmetic versus RSA encryption

The core textbook equations are correct:

$$
c=m^e\pmod n,
$$

$$
m=c^d\pmod n.
$$

But this is **textbook RSA**, not secure modern encryption.

Real RSA encryption uses an encoding/padding construction such as RSAES-OAEP. Raw modular exponentiation is deterministic and malleable and does not satisfy modern chosen-ciphertext security requirements.

So the canonical site keeps the modular arithmetic as an educational primitive while explicitly separating it from a secure encryption scheme.

## 3. CRT decryption: good idea, mostly correct algebra

The recovered CRT exercise computes

$$
m_p=c^{d\bmod(p-1)}\pmod p,
$$

$$
m_q=c^{d\bmod(q-1)}\pmod q,
$$

and combines the residues using Bézout coefficients.

If

$$
sp+tq=1,
$$

then

$$
qt\equiv1\pmod p,
$$

and

$$
ps\equiv1\pmod q.
$$

Therefore

$$
\boxed{
m=qt\,m_p+ps\,m_q\pmod{pq}
}
$$

is a correct CRT reconstruction.

Our cleaned lab preserves this idea and verifies that CRT decryption matches ordinary RSA decryption.

The engineering caveat is that production CRT-RSA must also defend against fault attacks; a single induced CRT fault can leak a prime factor if implementations do not verify results or apply appropriate countermeasures.

## 4. RSA common-modulus attack

The old workbook contains a useful attack example.

Suppose the same modulus $n$ and the same message $m$ are used with two public exponents:

$$
c_1=m^{e_1}\pmod n,
$$

$$
c_2=m^{e_2}\pmod n.
$$

If

$$
\gcd(e_1,e_2)=1,
$$

Bézout gives integers $a,b$ with

$$
ae_1+be_2=1.
$$

Then, when the required inverses exist,

$$
c_1^a c_2^b
\equiv
m^{ae_1+be_2}
\equiv
m
\pmod n.
$$

The old one-line expression

```python
c1^s * c2^t % n
```

hides an important implementation detail: one of $s,t$ is typically negative, so the corresponding ciphertext must be inverted modulo $n$.

Our cleaned Python version handles signed exponents explicitly.

## 5. Diffie–Hellman: the `bits` parameter was ignored

This is one of the clearest real bugs in the recovered workbook.

The function is called as

```python
generate_parameters(1024)
```

but internally it repeatedly samples with constants around

```python
2^8
2^10
```

and never uses `bits` to set the size of $q$.

So the interface says "generate a 1024-bit prime" while the implementation produces a tiny toy prime.

That is not merely insecure parameter selection; it is an interface/implementation contradiction.

The corrected lesson is:

1. choose a group with known large prime-order subgroup;
2. choose exponents as integers modulo the subgroup order;
3. validate public elements;
4. use cryptographically secure randomness;
5. derive a symmetric key from the shared group element with an appropriate KDF.

The toy companion deliberately uses a tiny subgroup only so every value can be inspected.

## 6. Full-group generator versus subgroup generator

The old comments alternate between wanting a generator of

$$
\mathbb Z_p^*
$$

and wanting a generator of the prime-order subgroup of size $q$ when

$$
p=2q+1.
$$

Those are not the same requirement.

For a safe prime $p=2q+1$:

- a generator of the full multiplicative group has order $2q$;
- an element in the quadratic-residue subgroup can have order $q$.

A protocol should specify which group it uses and validate keys accordingly.

Mixing those descriptions makes subgroup-security reasoning impossible.

## 7. The old "ElGamal" code is not textbook ElGamal

This is the most important naming correction in the public-key worksheet.

Textbook multiplicative ElGamal has public key

$$
y=g^x
$$

and encryption with fresh $k$:

$$
\boxed{
(c_1,c_2)
=
(g^k,
 m y^k)
}.
$$

Decryption computes

$$
m=c_2(c_1^x)^{-1}.
$$

The recovered exercise instead first performs a DH-style exchange to obtain a shared secret and then computes roughly

$$
c=m\cdot K.
$$

That is a multiplicative one-time masking step based on a DH-derived value. It does **not** by itself implement the ordinary ElGamal ciphertext pair.

Our canonical companion therefore uses the actual two-component ElGamal structure.

## 8. Why the pair matters

The receiver needs the ephemeral public value

$$
c_1=g^k
$$

in order to reconstruct

$$
c_1^x=g^{kx}=y^k.
$$

Without that value, the ciphertext does not contain enough information for ordinary ElGamal decryption unless some external protocol state already provides the same ephemeral secret.

This is a good example of why matching one algebraic multiplication is not enough to claim that a protocol has been implemented.

## 9. ECDH: structurally correct, but only a toy

The recovered ECDH exercise has the right core relation:

$$
A=aG,
\qquad
B=bG,
$$

and

$$
aB=abG=bA.
$$

That is the correct algebra.

What the short worksheet does not model is the protocol boundary:

- validate that a received point is on the intended curve;
- validate subgroup membership/cofactor requirements as appropriate;
- reject the identity;
- use secure scalar generation;
- serialize points canonically;
- pass the shared point through a KDF instead of using coordinates directly as application keys.

The distinction is the same one we have seen repeatedly throughout CryptoCave:

> **a correct group equation is not yet a complete cryptographic protocol.**

## 10. EC ElGamal and message encoding

The old notebook also contains elliptic-curve ElGamal:

$$
C_1=kG,
$$

$$
C_2=M+kQ,
$$

where

$$
Q=xG.
$$

Decryption is

$$
M=C_2-xC_1.
$$

That algebra is correct for a point-valued message $M$.

A following exercise uses a Koblitz-style method to search for an $x$ coordinate derived from an integer message until

$$
x^3+ax+b
$$

is a quadratic residue.

This is useful mathematical education, but it should not be mistaken for modern ECIES-style encryption. Modern systems generally avoid inventing ad-hoc message-to-point encryption layers and instead use KEM/DEM-style hybrid encryption.

## 11. Textbook RSA signatures: the worksheet attack is valid

The old signature exercise contains a very good lesson.

Textbook RSA verification checks

$$
s^e\equiv m\pmod n.
$$

An attacker can simply choose an arbitrary $s$ and define

$$
\boxed{m=s^e\pmod n}.
$$

Then $(m,s)$ verifies by construction.

This is an existential forgery against the raw textbook relation.

The attack does **not** mean secure RSA signatures are broken. Real signatures use a secure encoding such as RSASSA-PSS and sign a structured hash encoding, not an arbitrary integer message representative chosen after the signature.

Our cleaned lab retains this exact toy because it demonstrates why "sign by applying the private RSA exponent" is not a sufficient signature design.

## 12. Discrete logarithm exercises

The workbook uses Sage's built-in logarithm operation to recover small exponents.

For small classroom groups this is fine.

For cryptography, the correct security question is not whether Sage exposes a `.log()` method. The question is the asymptotic and concrete cost of the best DLP algorithm in the selected group.

That is why CryptoCave keeps BSGS, Pohlig–Hellman, Pollard rho, index calculus, and elliptic-curve DLP analysis in dedicated articles rather than interpreting a one-line Sage call as an attack model.

## 13. Old Python/Sage syntax hazards

Several old worksheets use Python 2 syntax:

```python
print x
```

and Sage-specific exponent syntax:

```python
x^e
```

Modern Python uses

```python
print(x)
```

and exponentiation is

```python
x ** e
```

with modular exponentiation preferably written

```python
pow(x, e, n)
```

for large integer cryptography.

Copying Sage syntax directly into a normal Python module can turn exponentiation into XOR and silently destroy the mathematics.

## 14. Clean canonical companion

The active experiment is

```text
experiments/sagemath-public-key-lab/public_key_lab.py
```

and verifies:

```text
PASS: RSA/CRT, common-modulus, DH, ElGamal, and textbook-signature toy checks
```

It intentionally does **not** attempt to become a cryptographic library.

Its job is to preserve the algebraic lessons with explicit toy-security labels.

## 15. What happened to the original Sage files?

They are not useful as canonical runtime dependencies:

- several are Python-2-era;
- much of the content duplicates stronger CryptoCave articles;
- some cells depend on notebook execution order;
- some parameter-generation code is wrong;
- several security claims are outdated or too broad.

The cleanup ledger records where each source was integrated, superseded, or discarded.

The useful concepts remain. The accidental environment and notebook state do not.

## Final lesson

The recovered workbook is a compact demonstration of the difference between three levels:

### Level 1 — algebraic identity

Examples:

$$
aB=bA,
$$

$$
c^d=m,
$$

$$
C_2-xC_1=M.
$$

### Level 2 — correctly implemented primitive

Correct parameter domains, inverses, encodings, and error handling.

### Level 3 — secure protocol

Padding/encoding standards, public-key validation, randomness requirements, KDFs, authentication, chosen-ciphertext security, replay/session handling, and side-channel resistance.

Most old educational code lives at Level 1 or 2.

The purpose of this audit is to preserve what it teaches without pretending it has already reached Level 3.
