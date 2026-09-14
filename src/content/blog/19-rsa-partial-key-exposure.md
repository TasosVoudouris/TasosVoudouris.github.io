---
title: 'RSA Deep Dive VII: Partial Key Exposure From Zero — When Known Bits Become a Small-Root Problem'
description: 'What does it really mean for part of an RSA secret to leak? We study the cleanest case first: known high bits of a prime factor. The remaining unknown suffix becomes a small root modulo an unknown divisor, connecting partial information directly to Coppersmith''s method.'
pubDate: '2026-09-10'
topics:
- Public-Key Cryptography
- Cryptanalysis
- Lattice Methods
tags:
- rsa
- partial-key-exposure
- coppersmith
- lattices
- factorization
- small-roots
- cryptanalysis
- cryptography-from-zero
difficulty: Advanced
series: RSA Deep Dives
seriesOrder: 7
draft: false
---
The previous Coppersmith article ended with several examples of the same pattern:

```text
secret structure
+
small unknown part
+
polynomial relation
=
small-root problem
```

One of those examples was:

$$
p=p_0+x.
$$

At the time I only mentioned it.

Now I want to stop there.

What does it really mean to know **part** of an RSA secret?

And why can a few known bits be more dangerous than they first appear?

The cleanest place to see the mathematics is not the private exponent yet.

It is one of the prime factors.

Suppose:

$$
N=pq
$$

is public, while $p$ and $q$ are secret.

Normally the factorization problem begins with almost no direct information about either factor.

Now suppose the high bits of $p$ are known.

Then $p$ is no longer an arbitrary hidden integer.

It has the form

$$
\boxed{
p=p_0+x
}
$$

where:

- $p_0$ is known,
- $x$ is unknown,
- but $x$ is **small**.

That is exactly the kind of representation Coppersmith's method wants.

![Partial RSA prime exposure becomes a small-root problem](/images/blog/19-rsa-partial-key-exposure.svg)

*The important transition is not “some bits leaked.” It is “the remaining uncertainty can be represented as a bounded polynomial root.”*

If you want the prerequisites first:

- [RSA Key Generation From Zero](/blog/12-rsa-key-generation/)
- [Coppersmith From Zero](/blog/17-rsa-coppersmith-from-zero/)
- [Boneh–Durfee From Zero](/blog/18-rsa-boneh-durfee/)

---

## 1. Start with the bit representation

Let $N$ be an $n$-bit RSA modulus:

$$
N=pq.
$$

For balanced two-prime RSA,

$$
p\approx q\approx\sqrt N.
$$

So each factor contains roughly

$$
\frac n2
$$

bits.

Write the binary representation of $p$ schematically as

```text
p = [ known high bits | unknown low bits ]
```

If the unknown suffix has $t$ bits, then

$$
p=p_0+x
$$

with

$$
0\le x<2^t.
$$

The number of unknown bits has become an ordinary numerical bound.

This is the first modelling step:

$$
\boxed{
\text{partial bit information}
\longrightarrow
\text{small integer unknown}.
}
$$

That seems simple, but it is the point where the leakage becomes algebra.

---

## 2. The polynomial appears almost immediately

Define

$$
f(x)=p_0+x.
$$

At the true unknown suffix $x_0$,

$$
f(x_0)=p.
$$

Since $p$ divides $N$,

$$
p\mid N.
$$

And of course,

$$
f(x_0)\equiv0\pmod p.
$$

Therefore we have:

$$
\boxed{
f(x_0)\equiv0\pmod p,
\qquad
p\mid N,
}
$$

where:

- $N$ is known,
- $f$ is known,
- $x_0$ is small,
- the modulus $p$ of the congruence is itself an **unknown divisor of $N$**.

That last point is what makes this problem different from the first Coppersmith example we studied.

There we had:

$$
f(x_0)\equiv0\pmod N.
$$

Here we have:

$$
f(x_0)\equiv0\pmod p
$$

for an unknown factor

$$
p\mid N.
$$

Coppersmith-style techniques can handle this divisor setting too.

---

## 3. The divisor small-root theorem

A useful modern way to state the relevant result is the following.

Suppose:

$$
p\mid N
$$

and

$$
p\ge N^\beta.
$$

Let $f(x)$ be a monic polynomial of degree $\delta$.

Then, with the usual asymptotic slack and parameter conditions, small roots satisfying

$$
f(x_0)\equiv0\pmod p
$$

can be recovered efficiently when the root is roughly below the scale

$$
\boxed{
|x_0|
\lesssim
N^{\beta^2/\delta}.
}
$$

Now specialize to balanced RSA.

Because:

$$
p\approx\sqrt N,
$$

we take

$$
\beta=\frac12.
$$

Our polynomial is linear:

$$
f(x)=p_0+x,
$$

so

$$
\delta=1.
$$

Therefore:

$$
N^{\beta^2/\delta}
=
N^{(1/2)^2}
=
N^{1/4}.
$$

So the critical scale becomes:

$$
\boxed{
|x_0|
\lesssim
N^{1/4}.
}
$$

That quarter-power should look familiar.

But notice what it means here.

It is **not** a small private exponent.

It is the size of the **unknown part of a prime factor**.

Same numerical exponent.

Different mathematical object.

---

## 4. Why this becomes “one quarter of the modulus bits”

Now translate the bound back into bits.

If $N$ has $n$ bits, then approximately

$$
N\approx2^n.
$$

Therefore:

$$
N^{1/4}
\approx
2^{n/4}.
$$

So if:

$$
|x_0|<N^{1/4},
$$

then the unknown suffix has roughly fewer than

$$
\frac n4
$$

bits.

A balanced prime factor has about

$$
\frac n2
$$

bits total.

Therefore knowing about the upper

$$
\frac n4
$$

bits of $p$ leaves about

$$
\frac n4
$$

bits unknown.

That is the famous partial-factor threshold.

Coppersmith's EUROCRYPT 1996 result showed that for an RSA modulus

$$
N=PQ,
$$

knowledge of roughly the high-order

$$
\frac14\log_2 N
$$

bits of one factor is enough for polynomial-time factor reconstruction.

Dan Boneh's RSA survey states the classical result in the memorable form:

> given either the $n/4$ most significant bits or the $n/4$ least significant bits of one RSA factor, the factorization can be reconstructed efficiently.

The important lesson is not the fraction by itself.

The chain is:

```text
known factor bits
        ↓
bounded unknown suffix
        ↓
small root modulo unknown divisor
        ↓
Coppersmith
        ↓
complete factor
```

---

## 5. A completely auditable toy model

Take two fixed 16-bit primes:

$$
p=60\,013,
$$

$$
q=61\,027.
$$

Then:

$$
N=pq
=
3\,662\,413\,351.
$$

This is a 32-bit modulus.

The binary representation of $p$ is:

```text
1110101001101101
```

Now suppose we keep only the high nine bits:

```text
111010100???????
```

The known prefix corresponds to:

$$
p_0=59\,904.
$$

Therefore:

$$
p=p_0+x_0
$$

with:

$$
x_0
=
60\,013-59\,904
=
109.
$$

So:

$$
\boxed{
p=59\,904+109.
}
$$

The polynomial is simply:

$$
f(x)=59\,904+x.
$$

At the hidden suffix:

$$
f(109)=60\,013=p.
$$

Hence:

$$
f(109)\equiv0\pmod{60\,013}.
$$

And:

$$
60\,013\mid3\,662\,413\,351.
$$

So the exact small-root model is present.

Now check the quarter-power scale:

$$
N^{1/4}
\approx246.00.
$$

Our unknown is:

$$
x_0=109.
$$

Therefore:

$$
\boxed{
109<N^{1/4}.
}
$$

The example is deliberately tiny and exposes slightly more prefix information than the asymptotic threshold would suggest, because finite toy parameters should not be confused with an asymptotic theorem.

The point is to make the geometry visible, not to claim that a 32-bit example reproduces asymptotic lattice behavior perfectly.

---

## 6. What the lattice has to accomplish

I do not want to rebuild the entire Coppersmith derivation here because we already did that.

But the scientific role of the lattice is worth stating again.

We know:

$$
f(x_0)\equiv0\pmod p
$$

for a large divisor

$$
p\mid N.
$$

The unknown $x_0$ is small.

Coppersmith-style constructions manufacture shifted polynomial relations whose evaluations at $x_0$ contain sufficiently large powers of the hidden divisor.

Then we:

```text
construct shifted polynomials
        ↓
scale x by the root bound X
        ↓
encode coefficients as lattice vectors
        ↓
apply LLL
        ↓
obtain a short integer polynomial
        ↓
force modular divisibility to become integer equality
        ↓
recover x0
```

The complication is that the relevant congruence is modulo $p$, while $p$ itself is unknown.

The lattice construction compensates for that by exploiting the known composite multiple:

$$
N.
$$

This is why the theorem needs a lower bound such as:

$$
p\ge N^\beta.
$$

We do not know the divisor.

But we know it is large.

That size information is part of the theorem.

---

## 7. Why this is scientifically different from brute force

For our 32-bit toy example, of course we could test:

```text
x = 0,1,2,...,127
```

until:

$$
p_0+x
$$

divides $N$.

That would work instantly.

But it would teach us almost nothing.

The scientific theorem says something asymptotic.

For a real $n$-bit modulus, the unknown suffix can itself contain about

$$
\frac n4
$$

bits.

A direct search would then cost roughly:

$$
2^{n/4}
$$

candidate tests.

That is exponential in the bit length.

Coppersmith's result replaces that exponential search, under the stated small-root conditions, with polynomial-time lattice computation.

So the important distinction is:

```text
toy verification:
small enough to inspect by hand

the theorem:
scales polynomially in log N
inside its mathematical root regime
```

The toy numbers are for understanding.

The theorem is the actual cryptanalytic result.

---

## 8. From partial factor exposure to partial private-exponent exposure

Now we can finally understand why the phrase **partial key exposure** became important in RSA research.

The classic Boneh–Durfee–Frankel result studies partial information about the private exponent $d$.

Start again from the RSA equation:

$$
ed-k\varphi(N)=1.
$$

Using:

$$
\varphi(N)=N-p-q+1,
$$

we obtain:

$$
ed-k(N-p-q+1)=1.
$$

Suppose some low bits of $d$ are known.

Then:

$$
ed
$$

is partially known modulo a suitable power of two.

For sufficiently small public exponent $e$, the possible integer $k$ lies in a manageable range.

The RSA equation can then be manipulated to obtain candidate partial information about one factor, such as bits of $p$.

At that point the previous theorem takes over:

```text
partial bits of d
        ↓
RSA key equation
        ↓
candidate partial bits of p
        ↓
Coppersmith partial-factor reconstruction
        ↓
factorization of N
        ↓
complete private key
```

Boneh, Durfee, and Frankel showed in 1998 that, for low-public-exponent RSA, a surprisingly small fraction of the private-key bits can determine the rest.

In the classical low-$e$ formulation highlighted by Boneh's survey, about the least-significant quarter of the bits of $d$ can suffice.

For larger public exponents the conditions and fractions change, and the analysis becomes more involved.

So we should not compress all partial-$d$ results into one slogan.

The useful conceptual point is:

> partial exposure becomes dangerous when the remaining uncertainty can be transformed into a mathematically small unknown.

That is the common language.

---

## 9. “Partial exposure” is an input model, not a leakage mechanism

There is another distinction I want to keep clear.

A partial-key-exposure theorem starts with an assumption like:

```text
these bits are known
```

It does not necessarily say **how** they became known.

That is a different research question.

The source of partial information might come from:

- an implementation defect,
- an information leak,
- a side channel,
- damaged or incomplete key material,
- memory remanence,
- protocol metadata,
- some other auxiliary information.

But the number-theoretic analysis begins **after** that information is available.

So there are two layers:

```text
information acquisition
        ↓
what partial information is available?

cryptanalytic reconstruction
        ↓
what can mathematics infer from it?
```

This post studies only the second layer.

That separation keeps the scientific model precise.

---

## 10. The deeper pattern: entropy is not the whole story

At first glance, knowing half of the bits of a prime might sound like we merely reduced the search space.

That would suggest:

```text
less uncertainty
=
faster brute force
```

But Coppersmith gives a much stronger lesson.

The location and algebraic form of the unknown information matter.

Knowing a structured prefix gives:

$$
p=p_0+x
$$

with small $x$.

That is more useful than knowing the same number of completely unstructured facts about $p$.

The representation interacts with:

$$
p\mid N.
$$

Together they create a polynomial congruence:

$$
p_0+x_0\equiv0\pmod p.
$$

So the real chain is:

$$
\boxed{
\text{information}
+
\text{algebraic structure}
+
\text{smallness}
\Longrightarrow
\text{efficient reconstruction}.
}
$$

This is a much broader cryptanalytic principle.

We will see it again in:

- related-message RSA,
- short-padding problems,
- Hidden Number Problems,
- partial nonce exposure,
- lattice attacks on signatures,
- approximate relations in post-quantum cryptanalysis.

The lattice does not create the weakness.

The lattice makes existing structure computationally accessible.

---

## 11. What I want to remember

For known high bits of one RSA prime:

$$
p=p_0+x_0.
$$

Define:

$$
f(x)=p_0+x.
$$

Because:

$$
p\mid N,
$$

we have:

$$
f(x_0)\equiv0\pmod p.
$$

For balanced RSA:

$$
p\approx N^{1/2}.
$$

For a degree-one polynomial, the relevant divisor small-root scale becomes:

$$
|x_0|
\lesssim
N^{1/4}.
$$

In bit language:

$$
N^{1/4}\approx2^{n/4}.
$$

Therefore the famous statement becomes:

```text
roughly n/4 known factor bits
        ↓
roughly n/4 unknown factor bits
        ↓
unknown suffix is in the small-root regime
        ↓
factor reconstruction
```

And the broader partial-$d$ literature uses RSA's key equation to turn some private-exponent leakage into this kind of factor information.

That is the scientific connection I wanted.

Not:

> “some bits leaked, therefore RSA is broken.”

But:

> “some bits leaked, and the remaining uncertainty now satisfies a polynomial relation inside a provable small-root regime.”

That is a much more useful statement.

---

## 12. Companion experiment

The companion script for this article remains deliberately narrow.

It checks only the mathematical model:

```text
1. construct fixed toy p and q
2. form N = pq
3. expose a high-bit prefix p0
4. compute the hidden suffix x0
5. verify p = p0 + x0
6. verify f(x0) = 0 mod p
7. verify p divides N
8. compare x0 with N^(1/4)
9. reconstruct p and q once x0 is supplied
```

It does not implement a generic key-recovery workflow.

The full lattice machinery belongs to the Coppersmith chapter we already built.

Here the goal is narrower:

**understand why partial bits become a small-root problem at all.**

---

## References

1. Don Coppersmith, **“Finding a Small Root of a Bivariate Integer Equation; Factoring with High Bits Known”**, *Advances in Cryptology — EUROCRYPT '96*, LNCS 1070, pp. 178–189, 1996.  
   https://doi.org/10.1007/3-540-68339-9_16

2. Don Coppersmith, **“Finding a Small Root of a Univariate Modular Equation”**, *Advances in Cryptology — EUROCRYPT '96*, LNCS 1070, pp. 155–165, 1996.  
   https://doi.org/10.1007/3-540-68339-9_14

3. Don Coppersmith, **“Small Solutions to Polynomial Equations, and Low Exponent RSA Vulnerabilities”**, *Journal of Cryptology*, 10(4), pp. 233–260, 1997.  
   https://doi.org/10.1007/s001459900030

4. Dan Boneh, Glenn Durfee, and Yair Frankel, **“An Attack on RSA Given a Small Fraction of the Private Key Bits”**, *ASIACRYPT '98*, LNCS 1514, pp. 25–34, 1998.  
   https://crypto.stanford.edu/~dabo/pubs/abstracts/bits_of_d.html

5. Dan Boneh, **“Twenty Years of Attacks on the RSA Cryptosystem”**, *Notices of the AMS*, 46(2), pp. 203–213, 1999.  
   https://crypto.stanford.edu/~dabo/abstracts/RSAattack-survey.html

---

We now have another Coppersmith pattern in concrete form:

```text
known message prefix  -> small plaintext suffix
known factor prefix   -> small prime suffix
small private d       -> bivariate small root
```

There is one more classical RSA case that connects these ideas beautifully.

What if two plaintexts are not partially known, but are **algebraically related**?

For example:

$$
m_2=am_1+b.
$$

Then polynomial GCDs over $\mathbb Z_N[x]$ suddenly become cryptanalytic objects.

**Next RSA Deep Dive:** *Franklin–Reiter From Zero — When Two Related RSA Messages Share an Algebraic Root.*
