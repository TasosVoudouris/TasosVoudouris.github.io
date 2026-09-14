---
title: 'RSA Deep Dive IX: Short-Pad RSA From Zero — Where Resultants, Coppersmith, and Franklin–Reiter Meet'
description: If the same textbook RSA message is sent twice with different but very short random pads, the relation between the padded representatives is unknown but small. We eliminate the message with a resultant, recover the small pad difference with Coppersmith's theorem, and then reuse Franklin–Reiter.
pubDate: '2026-09-10'
topics:
- Public-Key Cryptography
- Cryptanalysis
- Lattice Methods
tags:
- rsa
- coppersmith
- short-pad
- resultants
- franklin-reiter
- related-messages
- small-roots
- cryptanalysis
- cryptography-from-zero
difficulty: Advanced
series: RSA Deep Dives
seriesOrder: 9
draft: false
---
The previous post ended with a very clean situation.

Two textbook RSA messages satisfied a known relation:

$$
m_2=m_1+\Delta,
$$

and if $\Delta$ was known, Franklin–Reiter converted that relation into two polynomials with the same root.

Then polynomial Euclid recovered the shared root.

But a natural question remained.

What if the relation exists, but the offset itself is unknown?

That is exactly what happens in the classical **short-pad** setting.

Suppose the same underlying message $M$ is encoded twice by appending a small random pad:

$$
M_1=2^sM+r_1,
$$

$$
M_2=2^sM+r_2.
$$

The pads are different, so textbook RSA no longer sees the exact same representative.

At first this looks like randomness has fixed the repeated-message problem.

But if the pads are too short, then their difference

$$
\Delta=r_2-r_1
$$

is also small.

And now two ideas from the previous articles meet:

```text
unknown relation
but relation parameter is small
        ↓
eliminate the large message
        ↓
obtain one polynomial in Δ
        ↓
Coppersmith recovers small Δ
        ↓
Δ becomes known
        ↓
Franklin–Reiter recovers the padded message
```

This is one of the nicest places in classical RSA cryptanalysis where different algebraic tools genuinely compose.

![Short-pad RSA pipeline: resultant, Coppersmith, then Franklin-Reiter](/images/blog/21-rsa-short-pad.svg)

*The pad itself does not have to be recovered individually. It is enough to recover the small difference between two padded representatives.*

Relevant prerequisites:

- [Coppersmith From Zero](/blog/17-rsa-coppersmith-from-zero/)
- [Franklin–Reiter From Zero](/blog/20-rsa-franklin-reiter/)
- [Partial Key Exposure From Zero](/blog/19-rsa-partial-key-exposure/)

---

## 1. The short-pad model

Let the RSA public key be:

$$
(N,e).
$$

Take one message integer:

$$
M.
$$

Choose a pad length of $s$ bits.

Two independently padded representatives are:

$$
M_1=2^sM+r_1,
$$

$$
M_2=2^sM+r_2,
$$

where:

$$
0\le r_1,r_2<2^s.
$$

Textbook RSA gives:

$$
C_1\equiv M_1^e\pmod N,
$$

$$
C_2\equiv M_2^e\pmod N.
$$

Now subtract the two padded representatives:

$$
M_2-M_1=r_2-r_1.
$$

Define:

$$
\boxed{\Delta=r_2-r_1.}
$$

Therefore:

$$
\boxed{M_2=M_1+\Delta.}
$$

This is already the Franklin–Reiter relation.

The only difference from the previous post is crucial:

$$
\Delta
$$

is not known.

But because the pads are short,

$$
|\Delta|<2^s.
$$

So the unknown relation parameter is small.

That turns the problem into a Coppersmith problem.

---

## 2. Build two polynomials in two variables

For the classical case, take:

$$
e=3.
$$

Let $X$ represent the first padded message and let $Y$ represent the unknown pad difference.

Define:

$$
g_1(X,Y)=X^3-C_1,
$$

and:

$$
g_2(X,Y)=(X+Y)^3-C_2.
$$

At the true pair

$$
(X,Y)=(M_1,\Delta),
$$

we have:

$$
g_1(M_1,\Delta)\equiv0\pmod N,
$$

and:

$$
g_2(M_1,\Delta)\equiv0\pmod N.
$$

So the system contains two unknowns:

- the large padded message $M_1$,
- the small offset $\Delta$.

We only want the second one first.

This is where the **resultant** becomes useful.

---

## 3. What a resultant does

Take two polynomials:

$$
f(X,Y)
$$

and:

$$
g(X,Y).
$$

The resultant with respect to $X$,

$$
\operatorname{Res}_X(f,g),
$$

eliminates $X$.

The result is a polynomial only in $Y$.

The key property is:

> if the two original polynomials have a common root in $X$ for some value $Y=Y_0$, then the resultant vanishes at $Y_0$.

That is exactly our situation.

For:

$$
g_1=X^3-C_1,
$$

$$
g_2=(X+Y)^3-C_2,
$$

define:

$$
h(Y)=\operatorname{Res}_X(g_1,g_2).
$$

Because $X=M_1$ is a common root when $Y=\Delta$,

$$
\boxed{h(\Delta)\equiv0\pmod N.}
$$

The large unknown $M_1$ has disappeared.

We are left with one univariate modular polynomial whose root is the small pad difference.

That is the bridge to Coppersmith.

---

## 4. For $e=3$, the resultant has degree nine

For the cubic case the resultant can be written explicitly.

Starting from:

$$
g_1(X)=X^3-C_1,
$$

and:

$$
g_2(X,Y)=(X+Y)^3-C_2,
$$

eliminating $X$ gives:

$$
\boxed{
\begin{aligned}
h(Y)=\;&Y^9
+3(C_1-C_2)Y^6\\
&+3(C_1^2+7C_1C_2+C_2^2)Y^3\\
&+(C_1-C_2)^3.
\end{aligned}
}
$$

All coefficients are interpreted modulo $N$.

The important fact is the degree:

$$
\deg h=9.
$$

And:

$$
9=e^2
$$

when:

$$
e=3.
$$

This is where the famous short-pad scale comes from.

Coppersmith's univariate theorem says that a sufficiently small root of a monic degree-$9$ polynomial modulo $N$ is recoverable at the conceptual scale:

$$
|\Delta|\lesssim N^{1/9}.
$$

More generally, the short-pad construction produces a resultant whose relevant degree is at most about:

$$
e^2,
$$

so the root scale becomes:

$$
\boxed{|\Delta|\lesssim N^{1/e^2}.}
$$

That is why the pad must be very short.

---

## 5. Convert the root bound into pad bits

Let $N$ have $n$ bits.

Then approximately:

$$
N\approx2^n.
$$

Therefore:

$$
N^{1/e^2}\approx2^{n/e^2}.
$$

So the short-pad theorem naturally leads to a pad length on the scale:

$$
\boxed{s\approx\frac{n}{e^2}.}
$$

For:

$$
e=3,
$$

this becomes approximately:

$$
s\approx\frac n9.
$$

The useful interpretation is:

> for exponent three, a naive random suffix whose induced difference remains below the degree-nine Coppersmith root scale can be algebraically recoverable.

The exact theorem needs strict inequalities and asymptotic slack.

So I would not memorize:

```text
exactly n/9 bits = a hard boundary
```

The mathematical statement is the root condition:

$$
|\Delta|<N^{1/9}
$$

up to the usual theorem slack.

---

## 6. A fully checked 72-bit toy model

Choose two fixed 36-bit primes:

$$
p=68\,719\,476\,713,
$$

$$
q=68\,719\,476\,731.
$$

Then:

$$
N=pq
=
4\,722\,366\,480\,945\,499\,865\,203.
$$

This modulus has exactly:

$$
72
$$

bits.

Take:

$$
e=3.
$$

Then:

$$
\frac{72}{3^2}=8.
$$

So use an 8-bit padding space.

Choose the underlying message:

$$
M=12\,345\,678\,901\,234\,567.
$$

Take:

$$
r_1=37,
$$

$$
r_2=110.
$$

Then:

$$
M_1=2^8M+37
=
3\,160\,493\,798\,716\,049\,189,
$$

and:

$$
M_2=2^8M+110
=
3\,160\,493\,798\,716\,049\,262.
$$

Their difference is:

$$
\boxed{\Delta=73.}
$$

Now encrypt:

$$
C_1
=
M_1^3\bmod N
=
2\,864\,700\,865\,949\,590\,458\,710,
$$

$$
C_2
=
M_2^3\bmod N
=
2\,517\,680\,417\,894\,642\,341\,351.
$$

The ninth-root scale is:

$$
N^{1/9}\approx256.
$$

And:

$$
73<256.
$$

So our offset sits comfortably inside the degree-nine small-root scale.

---

## 7. Verify the resultant root

For these ciphertexts, reduce the resultant coefficients modulo $N$.

We obtain:

$$
h(Y)
=
Y^9+a_6Y^6+a_3Y^3+a_0
\pmod N.
$$

The companion script computes the exact modular coefficients.

Now evaluate at:

$$
Y=73.
$$

The result is:

$$
\boxed{h(73)\equiv0\pmod N.}
$$

This is the critical checkpoint.

Before invoking any small-root algorithm, we have verified that the unknown pad difference is genuinely a modular root of the univariate polynomial produced by elimination.

The mathematical pipeline is now:

```text
two ciphertext equations
        ↓
resultant eliminates M1
        ↓
h(Δ) = 0 mod N
        ↓
|Δ| < N^(1/9)
```

This is exactly the input shape required by the Coppersmith machinery built earlier.

---

## 8. Why we do not rebuild LLL here

At this point we could repeat:

```text
shifted polynomials
coefficient scaling
lattice basis
LLL
short polynomial
integer-zero argument
root extraction
```

But that would duplicate the Coppersmith chapter.

The genuinely new modelling step here is:

$$
\boxed{\text{resultant}}
$$

because it transforms a problem in:

$$
(M_1,\Delta)
$$

into a univariate equation involving only:

$$
\Delta.
$$

So keep the stages separate:

### Stage A — elimination

$$
h(Y)=\operatorname{Res}_X(g_1,g_2).
$$

### Stage B — small-root recovery

Use univariate Coppersmith for:

$$
\Delta.
$$

### Stage C — related-message recovery

Once $\Delta$ is known, return to Franklin–Reiter.

This modular view is much clearer than hiding all three inside one library function.

---

## 9. Once $\Delta$ is known, Franklin–Reiter finishes the algebra

After the small-root stage recovers:

$$
\Delta=73,
$$

the relation becomes completely known:

$$
M_2=M_1+73.
$$

Define:

$$
f_1(X)=X^3-C_1,
$$

$$
f_2(X)=(X+73)^3-C_2.
$$

Both have common root:

$$
X=M_1.
$$

So compute:

$$
\gcd(f_1,f_2)
$$

over:

$$
\mathbb Z_N[X].
$$

For the toy example, the monic GCD is:

$$
\boxed{X-M_1.}
$$

Therefore:

$$
M_1
=
3\,160\,493\,798\,716\,049\,189.
$$

Now remember:

$$
M_1=2^8M+r_1.
$$

Because:

$$
0\le r_1<2^8,
$$

integer division by $2^8$ removes the suffix:

$$
M=
\left\lfloor
\frac{M_1}{256}
\right\rfloor.
$$

Hence:

$$
\boxed{
M=12\,345\,678\,901\,234\,567.
}
$$

The complete reconstruction is therefore:

```text
resultant
    ↓
small Δ
    ↓
Franklin–Reiter
    ↓
M1
    ↓
remove low s bits
    ↓
M
```

---

## 10. Three algebraic tools, three different jobs

This example composes three mechanisms.

### Resultants

They eliminate the large unknown variable.

### Coppersmith

It recovers the sufficiently small modular root.

### Franklin–Reiter

It recovers the shared message root once the affine relation is known.

Their interfaces line up:

$$
\boxed{
\operatorname{Resultant}
\rightarrow
\operatorname{Coppersmith}
\rightarrow
\operatorname{Franklin\text{-}Reiter}.
}
$$

That architecture is more important than memorizing three attack names.

---

## 11. What if the pad difference is larger?

Suppose:

$$
|\Delta|\ge N^{1/9}.
$$

The resultant still exists.

And:

$$
h(\Delta)\equiv0\pmod N
$$

still holds.

What changes is the theorem guarantee.

The root has left the standard degree-nine univariate Coppersmith range used by this argument.

So the scientifically correct statement is not:

> recovery is now impossible.

It is:

> this particular sufficient small-root theorem no longer guarantees efficient recovery.

There may be additional structure, more observations, or different algebraic models.

Failure of one theorem is not a proof of hardness.

---

## 12. Short random suffixes are not OAEP

The vulnerable encoding here is essentially:

$$
2^sM+r.
$$

It appends a few random bits to an otherwise algebraically exposed representative.

RSAES-OAEP is fundamentally different.

OAEP applies a structured randomized encoding before RSA exponentiation, involving a fresh seed, hashing and mask-generation operations.

So the conclusion is not:

> randomness does not help RSA.

It is:

> a small random suffix does not necessarily destroy the low-degree algebraic relation exposed by textbook RSA.

This is another reason to distinguish:

$$
\text{RSA primitive}
$$

from:

$$
\text{RSA encryption scheme}.
$$

---

## 13. What I want to remember

Start with:

$$
M_1=2^sM+r_1,
$$

$$
M_2=2^sM+r_2.
$$

Define:

$$
\Delta=r_2-r_1.
$$

Then:

$$
M_2=M_1+\Delta.
$$

For exponent three:

$$
g_1(X)=X^3-C_1,
$$

$$
g_2(X,Y)=(X+Y)^3-C_2.
$$

Eliminate $X$:

$$
h(Y)=\operatorname{Res}_X(g_1,g_2).
$$

Then:

$$
h(\Delta)\equiv0\pmod N,
$$

and:

$$
\deg h=9.
$$

If the small-root condition holds:

$$
|\Delta|\lesssim N^{1/9},
$$

Coppersmith recovers $\Delta$.

Then:

$$
\gcd
\left(
X^3-C_1,
(X+\Delta)^3-C_2
\right)
=
X-M_1
$$

in the generic Franklin–Reiter case.

Finally:

$$
M=
\left\lfloor
\frac{M_1}{2^s}
\right\rfloor.
$$

The mental model is:

```text
same message
+ two short random suffixes
        ↓
small unknown difference
        ↓
resultant
        ↓
univariate modular root
        ↓
Coppersmith
        ↓
known relation
        ↓
Franklin–Reiter
        ↓
original message representative
```

---

## References

1. Don Coppersmith, **“Small Solutions to Polynomial Equations, and Low Exponent RSA Vulnerabilities”**, *Journal of Cryptology*, 10(4), pp. 233–260, 1997.  
   https://doi.org/10.1007/s001459900030

2. Don Coppersmith, Matthew Franklin, Jacques Patarin, and Michael Reiter, **“Low-Exponent RSA with Related Messages”**, *EUROCRYPT '96*, LNCS 1070, pp. 1–9, 1996.  
   https://doi.org/10.1007/3-540-68339-9_1

3. Dan Boneh, **“Twenty Years of Attacks on the RSA Cryptosystem”**, *Notices of the AMS*, 46(2), pp. 203–213, 1999.  
   https://crypto.stanford.edu/~dabo/abstracts/RSAattack-survey.html

4. Matthew K. Franklin and Michael K. Reiter, **“A Linear Protocol Failure for RSA with Exponent Three”**, CRYPTO '95 Rump Session, 1995.

---

The algebraic low-exponent branch is now nearly complete.

We have:

```text
same plaintext / different moduli
    -> Håstad

same modulus / different exponents
    -> common modulus

known related messages
    -> Franklin–Reiter

unknown but small relation
    -> resultant + Coppersmith + Franklin–Reiter
```

The next RSA topic changes layer.

Instead of exploiting a polynomial relation in the plaintext, the next question is what mathematical information can be extracted if a receiver reveals whether a decrypted encoding belongs to a particular validity set.

That takes us from algebraic cryptanalysis into adaptive oracle cryptanalysis.

**Next RSA Deep Dive:** *Bleichenbacher From Zero — From a Validity Predicate to Adaptive Interval Narrowing.*
