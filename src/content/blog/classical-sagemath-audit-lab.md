---
title: "Classical Cryptanalysis II: Auditing an Old SageMath Lab — Shift, Substitution, Affine, Hill, and Algebraic Failure Modes"
description: "A forensic cleanup of recovered classical-cryptography coursework: what the Sage code intended, which equations are correct, where terminology and algebra went wrong, and corrected runnable implementations."
pubDate: "2016-12-22"
updatedDate: "2026-09-14"
topics:
- "Classical Cryptography"
- "Cryptanalysis"
- "Mathematical Foundations"
- "Cryptographic Engineering"
tags:
- "sagemath"
- "shift-cipher"
- "substitution-cipher"
- "affine-cipher"
- "hill-cipher"
- "known-plaintext"
- "code-audit"
difficulty: "Introductory"
status: "Validated"
series: "Classical Cryptanalysis"
seriesOrder: 2
sourcePath: "experiments/classical-cryptanalysis/sagemath-lab"
draft: false
---
Old cryptography coursework is valuable for an unusual reason: it preserves not only the mathematics we were trying to learn, but also the mistakes that reveal which distinctions were not yet clear.

The recovered SageMath notebooks in this batch contain shift ciphers, alphabet permutations, affine ciphers, Hill ciphers, known-plaintext attacks, and several home-grown cryptanalysis functions. Much of the intuition is good. Several details are not.

Rather than publish the notebook unchanged, this article uses it as a code-audit case study.

![Recovered classical Sage worksheet to audited canonical lab](/images/blog/sagemath/classical-lab-audit.svg)

## 1. First cleanup: substitution is not transposition

One exercise is titled "Transposition Cipher" but then defines a key as a permutation

$$
\pi:\mathbb Z_{26}\to\mathbb Z_{26}
$$

and encrypts each symbol independently as

$$
E_\pi(x)=\pi(x).
$$

That is a **monoalphabetic substitution cipher**.

A transposition cipher instead preserves the symbols and permutes their positions.

The distinction matters:

- substitution changes symbol identities but preserves position structure;
- transposition changes positions but preserves symbol frequencies exactly;
- the corresponding cryptanalytic techniques differ.

This is a terminology error, not merely a naming preference.

## 2. Shift cipher: correct and useful

For the Caesar/shift family,

$$
E_k(x)=x+k\pmod{26},
$$

$$
D_k(y)=y-k\pmod{26}.
$$

The old code translates letters to $0,\ldots,25$, adds the key, and converts back.

That part is structurally correct.

The security lesson is also correct: there are only 26 possible shifts, so exhaustive search completely defeats the scheme.

The better modern phrasing is not simply "modulo 26 is insecure." Modular arithmetic itself is not the weakness. The weakness is that the key space contains only 26 transformations and the ciphertext preserves enormous language structure.

## 3. Monoalphabetic substitution: large key space, weak structure

A monoalphabetic substitution has

$$
26!
$$

possible keys, so naive brute force is enormous.

Yet it is still insecure because it preserves:

- single-letter frequencies;
- repeated-letter patterns;
- digrams and trigrams;
- word-shape structure.

This is a classic demonstration that

$$
\boxed{\text{large key space}\not\Rightarrow\text{secure cipher}}.
$$

The old notebook correctly begins from frequency counts and then manually refines the mapping. What it does not make explicit is that frequency analysis is a statistical inference problem, not simply "map the most common ciphertext letter to E."

## 4. Affine cipher

The affine cipher is

$$
E_{a,b}(x)=ax+b\pmod{26},
$$

with the requirement

$$
\gcd(a,26)=1.
$$

Only then does $a^{-1}\pmod{26}$ exist, giving

$$
D_{a,b}(y)=a^{-1}(y-b)\pmod{26}.
$$

The recovered worksheet mostly uses this correctly, but one of its most interesting exercises exposes an algebra bug.

## 5. Double affine encryption collapses to one affine map

Suppose

$$
E_1(x)=a_1x+b_1
$$

and then

$$
E_2(x)=a_2x+b_2.
$$

Composition gives

$$
E_2(E_1(x))
=
a_2(a_1x+b_1)+b_2.
$$

Therefore

$$
E_2(E_1(x))
=
(a_2a_1)x+(a_2b_1+b_2)
\pmod{26}.
$$

So the equivalent single affine key is

$$
\boxed{
a_3=a_2a_1\pmod{26}
}
$$

and

$$
\boxed{
b_3=a_2b_1+b_2\pmod{26}.
}
$$

For the worksheet values

$$
a_1=3,
\quad b_1=5,
\quad a_2=11,
\quad b_2=7,
$$

we get

$$
a_3=11\cdot3=33\equiv7\pmod{26},
$$

$$
b_3=11\cdot5+7=62\equiv10\pmod{26}.
$$

Thus

$$
\boxed{(a_3,b_3)=(7,10)}.
$$

The old notebook instead ended up testing $(20,10)$ after a failed linear solve. That is simply incorrect.

Our cleaned executable test now proves

```text
E_(11,7)(E_(3,5)("K")) == E_(7,10)("K")
```

exactly.

## 6. The deeper lesson: closure destroys the hoped-for gain

The reason double affine encryption gives no new family is algebraic closure.

The set of invertible affine maps of $\mathbb Z_{26}$ is closed under composition.

Therefore applying two affine maps does not move us into a larger transformation family. It simply produces another affine map.

This is different from the generic meet-in-the-middle phenomenon for double encryption. Here the failure is even stronger: the two-layer construction collapses algebraically to one layer.

## 7. Known-plaintext recovery of an affine key

Given two plaintext/ciphertext pairs

$$
(x_1,y_1),
\qquad
(x_2,y_2),
$$

we have

$$
y_1=ax_1+b,
$$

$$
y_2=ax_2+b
\pmod{26}.
$$

Subtract:

$$
y_1-y_2=a(x_1-x_2)\pmod{26}.
$$

If

$$
\gcd(x_1-x_2,26)=1,
$$

then

$$
a=(y_1-y_2)(x_1-x_2)^{-1}\pmod{26},
$$

and

$$
b=y_1-ax_1\pmod{26}.
$$

So two suitable known plaintext symbols are enough.

The qualification "suitable" matters because $\mathbb Z_{26}$ is not a field. Some nonzero differences are noninvertible.

## 8. Hill cipher: linear algebra over Z_26

For a block vector $x\in\mathbb Z_{26}^d$ and key matrix $K$,

$$
E_K(x)=Kx\pmod{26}.
$$

The key is valid only if $K$ is invertible modulo 26.

For a $2\times2$ matrix, the condition is

$$
\boxed{\gcd(\det K,26)=1}.
$$

A nonzero determinant as an ordinary integer is not enough. The determinant must be a unit in $\mathbb Z_{26}$.

Our cleaned lab implements this check explicitly and rejects invalid keys rather than relying on a later inversion error.

## 9. A position-dependent affine toy

One exercise uses

$$
C_i=ai+bM_i+c\pmod N.
$$

This is still linear in the unknown key components $(a,b,c)$.

With three known plaintext/ciphertext equations we can write

$$
\begin{pmatrix}
1&M_1&1\\
2&M_2&1\\
3&M_3&1
\end{pmatrix}
\begin{pmatrix}
a\\b\\c
\end{pmatrix}
=
\begin{pmatrix}
C_1\\C_2\\C_3
\end{pmatrix}
\pmod N.
$$

If the coefficient matrix is invertible over the modular ring, key recovery is immediate.

The old worksheet tries to derive a hand formula and notes that it does not recover the original key. The right repair is not to keep manipulating signs until the expected answer appears. It is to solve the modular linear system while checking invertibility conditions.

That is a good general cryptanalytic habit:

> if a construction is linear in the secret parameters, write the observations as a linear system before inventing an attack-specific formula.

## 10. Python-versus-Sage operator trap

The old material repeatedly uses syntax such as

```python
x^e
```

for exponentiation.

Inside SageMath this is accepted as exponentiation.

In normal Python,

```python
^
```

means bitwise XOR.

The portable Python spelling is

```python
x ** e
```

or, for modular exponentiation,

```python
pow(x, e, n)
```

This is one of the easiest ways for old Sage code to become silently wrong when copied into a modern Python project.

## 11. Cleaned executable lab

The canonical companion is

```text
experiments/classical-cryptanalysis/sagemath-lab/classical_lab.py
```

and currently verifies:

```text
PASS: shift, affine composition, and Hill-cipher checks
```

It intentionally keeps only the useful core:

- shift encryption/decryption;
- affine encryption/decryption;
- exact affine-composition derivation;
- Hill-cipher inversion conditions.

The original giant notebook is not needed in the canonical repository once those lessons have been extracted.

## 12. Why retain these old exercises at all?

Because they expose three lessons that remain relevant in modern cryptography:

### Algebraic closure can defeat "more rounds"

If the construction family is closed under composition, stacking instances may add no security at all.

### Invertibility conditions are part of the cryptosystem

A formula such as

$$
a^{-1}\pmod n
$$

is not defined for every nonzero $a$ when the modulus is composite.

### Correct code is not the same as secure cryptography

An affine or Hill implementation can be perfectly correct and still completely insecure.

That distinction becomes even more important in modern cryptography, where a mathematically correct primitive can still fail because of nonce reuse, malformed encodings, side channels, missing authentication, or weak composition.
