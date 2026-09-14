---
title: 'RSA Deep Dive IV: Wiener''s Attack From Zero'
description: Continued fractions look like pure number theory until an unusually small RSA private exponent turns k/d into a recoverable convergent of e/N. We derive the approximation, recover d, factor N, implement the attack, and test its failure boundary.
pubDate: '2026-09-09'
topics:
- Public-Key Cryptography
- Cryptanalysis
- Number Theory
tags:
- rsa
- wiener-attack
- continued-fractions
- small-private-exponent
- cryptanalysis
- number-theory
- cryptography-from-zero
difficulty: Advanced
series: RSA Deep Dives
seriesOrder: 4
draft: false
---
Until now, our RSA attacks have exploited public-side structure:

- raw textbook algebra,
- repeated moduli,
- repeated messages,
- small public exponents.

This time the public key looks completely ordinary.

The weakness is hidden inside the **private exponent**.

Suppose somebody notices that RSA private operations compute:

$$
m=c^d\bmod N.
$$

Smaller $d$ means fewer exponent bits.

Fewer exponent bits can mean faster decryption or signing.

So an engineer might ask:

> Why not deliberately choose a very small private exponent?

That optimization can destroy RSA.

Michael Wiener's attack shows that, under a classical balanced-prime setting, a sufficiently small $d$ leaves such a strong rational approximation inside the public key $(N,e)$ that **continued fractions recover the private exponent in polynomial time**.

That sentence is worth reading twice.

The attacker does not:

- factor $N$ first,
- brute-force $d$,
- query a decryption oracle,
- observe timing,
- inject faults.

The attacker computes a continued-fraction expansion of the **public ratio**:

$$
\frac{e}{N}.
$$

One of its convergents reveals:

$$
\frac{k}{d}.
$$

Then $d$ falls out.

This is exactly the kind of path I want CryptoCave to preserve:

```text
Euclidean algorithm
        ↓
continued fractions
        ↓
Diophantine approximation
        ↓
RSA key equation
        ↓
private-key recovery
```

If you want to refresh earlier foundations:

- [GCD and Euclid](/blog/01-integers-division-and-gcd/)
- [Extended Euclid and Bézout](/blog/02-extended-euclid-bezout-modular-inverse/)
- [RSA Key Generation From Zero](/blog/12-rsa-key-generation/)
- [RSA Deep Dive III: Håstad's Broadcast Attack](/blog/15-rsa-hastad-broadcast-attack/)

![Wiener's attack: continued fractions reveal a small RSA private exponent](/images/blog/16-rsa-wiener-attack.svg)

*The RSA key equation makes $k/d$ extremely close to the public value $e/N$. When $d$ is small enough, continued fractions are forced to expose that rational approximation as a convergent.*

---

## 1. Before RSA: what is a continued fraction?

Take a rational number:

$$
\frac{43}{19}.
$$

Ordinary division gives:

$$
43=2\cdot19+5.
$$

So:

$$
\frac{43}{19}
=
2+\frac{5}{19}
=
2+\frac{1}{19/5}.
$$

Now divide again:

$$
19=3\cdot5+4.
$$

Therefore:

$$
\frac{19}{5}
=
3+\frac45
=
3+\frac{1}{5/4}.
$$

Continue:

$$
5=1\cdot4+1,
$$

and:

$$
4=4\cdot1.
$$

So:

$$
\frac{43}{19}
=
2+\cfrac{1}{
3+\cfrac{1}{
1+\cfrac{1}{4}
}
}.
$$

We write this compactly as:

$$
\boxed{
\frac{43}{19}=[2;3,1,4].
}
$$

The values:

$$
2,\ 3,\ 1,\ 4
$$

are called **partial quotients**.

And notice something familiar.

The partial quotients came directly from Euclidean division.

So continued fractions are not a completely new algorithm.

They are another view of the Euclidean algorithm.

---

## 2. Convergents: unusually good rational approximations

If we stop a continued fraction early, we obtain its **convergents**.

For:

$$
[2;3,1,4],
$$

the convergents are:

$$
2,
$$

$$
2+\frac13=\frac73,
$$

$$
2+\cfrac{1}{3+\frac11}
=
\frac94,
$$

and finally:

$$
\frac{43}{19}.
$$

Convergents are not arbitrary truncations.

They have remarkable approximation properties.

A standard recurrence computes them efficiently.

Let the continued fraction be:

$$
[a_0;a_1,a_2,\ldots].
$$

Define numerators $h_i$ and denominators $k_i$ by:

$$
h_{-2}=0,\qquad h_{-1}=1,
$$

$$
k_{-2}=1,\qquad k_{-1}=0.
$$

Then:

$$
h_i=a_i h_{i-1}+h_{i-2},
$$

$$
k_i=a_i k_{i-1}+k_{i-2}.
$$

The $i$-th convergent is:

$$
\boxed{
\frac{h_i}{k_i}.
}
$$

That recurrence will appear almost unchanged in our Python code.

---

## 3. The approximation theorem we need

The bridge from continued fractions to cryptanalysis is a classical Diophantine-approximation result usually associated with Legendre.

A useful form says:

> If a reduced fraction $a/b$ approximates a real number $x$ so well that
>
> $$
> \left|x-\frac{a}{b}\right|
> <
> \frac{1}{2b^2},
> $$
>
> then $a/b$ must appear as a convergent of the continued-fraction expansion of $x$.

This theorem is exactly what Wiener needs.

We will try to prove that the secret fraction:

$$
\frac{k}{d}
$$

is so close to the public ratio:

$$
\frac{e}{N}
$$

that it is forced to appear among the convergents.

Then we simply enumerate the convergents.

No brute force over all possible $d$.

The approximation theorem has already reduced the search to a tiny structured list.

---

## 4. Return to the RSA key equation

For the classical Wiener derivation, write RSA using:

$$
N=pq
$$

and:

$$
ed\equiv1\pmod{\varphi(N)}.
$$

Therefore there exists an integer $k$ such that:

$$
\boxed{
ed-k\varphi(N)=1.
}
$$

Rearrange:

$$
ed-1=k\varphi(N).
$$

Divide by:

$$
d\varphi(N).
$$

We obtain:

$$
\frac{e}{\varphi(N)}
-
\frac{k}{d}
=
\frac{1}{d\varphi(N)}.
$$

Therefore:

$$
\boxed{
\left|
\frac{e}{\varphi(N)}
-
\frac{k}{d}
\right|
=
\frac{1}{d\varphi(N)}.
}
$$

So $k/d$ is already an astonishingly good approximation to:

$$
\frac{e}{\varphi(N)}.
$$

There is only one problem.

The attacker does not know:

$$
\varphi(N).
$$

If they knew $\varphi(N)$, RSA would already be essentially broken.

The attacker knows:

$$
N
$$

instead.

So the key question becomes:

> Is $N$ close enough to $\varphi(N)$ that $e/N$ still approximates $k/d$ extremely well?

For balanced RSA primes, yes.

---

## 5. Why $N$ approximates $\varphi(N)$

For:

$$
N=pq,
$$

Euler's totient is:

$$
\varphi(N)
=
(p-1)(q-1).
$$

Expand:

$$
\varphi(N)
=
pq-p-q+1.
$$

Since:

$$
pq=N,
$$

we have:

$$
\boxed{
\varphi(N)=N-(p+q)+1.
}
$$

Therefore:

$$
N-\varphi(N)
=
p+q-1.
$$

For balanced RSA primes $p$ and $q$, both are roughly:

$$
\sqrt N.
$$

So:

$$
p+q
$$

is only on the order of:

$$
\sqrt N.
$$

Compared with $N$, that difference is small.

In Wiener's classical theorem, assume:

$$
q<p<2q.
$$

Then one can bound:

$$
p+q-1<3\sqrt N.
$$

Hence:

$$
\boxed{
|N-\varphi(N)|<3\sqrt N.
}
$$

So replacing $\varphi(N)$ with $N$ introduces only a relatively small error.

That is the approximation leak.

---

## 6. Derive the public approximation

Start from:

$$
ed-k\varphi(N)=1.
$$

We want:

$$
\left|
\frac{e}{N}
-
\frac{k}{d}
\right|.
$$

Bring the fractions together:

$$
\frac{e}{N}
-
\frac{k}{d}
=
\frac{ed-kN}{Nd}.
$$

Now replace $ed$ using:

$$
ed=1+k\varphi(N).
$$

Then:

$$
ed-kN
=
1+k\varphi(N)-kN.
$$

So:

$$
ed-kN
=
1-k(N-\varphi(N)).
$$

Therefore:

$$
\left|
\frac{e}{N}
-
\frac{k}{d}
\right|
=
\frac{
|1-k(N-\varphi(N))|
}{
Nd
}.
$$

For the usual theorem assumptions, $k<d$.

Using:

$$
N-\varphi(N)<3\sqrt N,
$$

we obtain the rough bound:

$$
\left|
\frac{e}{N}
-
\frac{k}{d}
\right|
<
\frac{3}{\sqrt N}.
$$

Now suppose:

$$
\boxed{
d<\frac13N^{1/4}.
}
$$

Then:

$$
d^2<\frac19\sqrt N.
$$

Hence:

$$
\frac{1}{2d^2}
>
\frac{9}{2\sqrt N}.
$$

And:

$$
\frac{3}{\sqrt N}
<
\frac{9}{2\sqrt N}.
$$

So:

$$
\boxed{
\left|
\frac{e}{N}
-
\frac{k}{d}
\right|
<
\frac{1}{2d^2}.
}
$$

Legendre's approximation theorem now applies.

Therefore:

$$
\boxed{
\frac{k}{d}
\text{ must be a convergent of }
\frac{e}{N}.
}
$$

That is Wiener's attack in one sentence.

The small private exponent forces the secret rational number $k/d$ into a publicly computable continued-fraction sequence.

---

## 7. A careful note about the famous bound

You will often read:

```text
Wiener's attack works when d < N^(1/4)
```

That is a useful memory aid, but it is too loose as a theorem statement.

A clean classical sufficient theorem commonly presented in the RSA literature is:

$$
q<p<2q,
$$

$$
e<\varphi(N),
$$

and:

$$
\boxed{
d<\frac13N^{1/4}.
}
$$

Under those conditions, continued fractions recover $d$ efficiently.

There are later refinements and generalized analyses of the boundary.

So in this project I want to distinguish three things:

```text
heuristic slogan:
d is dangerously around the N^(1/4) scale

classical sufficient theorem:
d < N^(1/4)/3 under balanced-prime assumptions

later work:
refines / extends the exact vulnerable region
```

This matters because cryptanalytic bounds are not decoration.

They are part of the attack model.

---

## 8. Full vulnerable RSA example

Now let us run the attack on a completely auditable key.

Take:

$$
p=379,
\qquad
q=239.
$$

Then:

$$
N=pq=90{,}581.
$$

The totient is:

$$
\varphi(N)
=
378\cdot238
=
89{,}964.
$$

Deliberately choose the tiny private exponent:

$$
\boxed{d=5}.
$$

Choose the public exponent so that:

$$
ed\equiv1\pmod{\varphi(N)}.
$$

One valid value is:

$$
e=17{,}993.
$$

Check:

$$
17{,}993\cdot5
=
89{,}965
=
89{,}964+1.
$$

Thus:

$$
\boxed{
ed-\varphi(N)=1.
}
$$

So here:

$$
k=1.
$$

The public key is only:

$$
\boxed{
(N,e)=(90{,}581,\ 17{,}993).
}
$$

The attacker does not know:

$$
p=379,
$$

$$
q=239,
$$

or:

$$
d=5.
$$

Now attack it.

---

## 9. Continued fraction of the public value $e/N$

Compute:

$$
\frac{e}{N}
=
\frac{17{,}993}{90{,}581}.
$$

Run Euclid.

The continued-fraction expansion is:

$$
\boxed{
\frac{17{,}993}{90{,}581}
=
[0;5,29,4,1,3,2,4,3].
}
$$

Its convergents are:

$$
\frac01,
$$

$$
\frac15,
$$

$$
\frac{29}{146},
$$

$$
\frac{117}{589},
$$

$$
\frac{146}{735},
$$

$$
\frac{555}{2794},
$$

$$
\frac{1256}{6323},
$$

$$
\frac{5579}{28086},
$$

and finally:

$$
\frac{17993}{90581}.
$$

Look at the second convergent:

$$
\boxed{
\frac15.
}
$$

That is exactly:

$$
\frac{k}{d}.
$$

So the denominator immediately gives the private exponent candidate:

$$
\boxed{d=5}.
$$

But a cryptanalytic program should not trust a candidate simply because it appeared in the list.

It should **validate it algebraically**.

---

## 10. How do we validate a candidate $(k,d)$?

Suppose a convergent gives a candidate:

$$
\frac{k}{d}.
$$

From the RSA key equation:

$$
ed-k\varphi(N)=1.
$$

Solve for the totient:

$$
\boxed{
\varphi(N)=\frac{ed-1}{k}.
}
$$

For:

$$
k=1,
\qquad
d=5,
$$

we obtain:

$$
\varphi(N)
=
17{,}993\cdot5-1
=
89{,}964.
$$

Now remember:

$$
\varphi(N)=N-(p+q)+1.
$$

So:

$$
p+q
=
N-\varphi(N)+1.
$$

Define:

$$
S=N-\varphi(N)+1.
$$

For our candidate:

$$
S
=
90{,}581-89{,}964+1
=
618.
$$

We also know:

$$
pq=N.
$$

Therefore $p$ and $q$ are the roots of:

$$
x^2-Sx+N=0.
$$

That is:

$$
x^2-618x+90{,}581=0.
$$

The discriminant is:

$$
\Delta
=
S^2-4N.
$$

Compute:

$$
\Delta
=
618^2
-
4(90{,}581).
$$

So:

$$
\Delta=19{,}600.
$$

And:

$$
19{,}600=140^2.
$$

Therefore the roots are integers:

$$
p
=
\frac{618+140}{2}
=
379,
$$

$$
q
=
\frac{618-140}{2}
=
239.
$$

We recovered the factorization too.

So candidate validation gives us a very strong condition:

```text
(ed - 1) divisible by k
        ↓
candidate phi(N)
        ↓
candidate S = p + q
        ↓
perfect-square discriminant
        ↓
p*q == N
```

If all of those checks pass, we have not merely guessed a small $d$.

We have reconstructed a consistent RSA private key.

---

## 11. The attack algorithm

The algorithm now becomes surprisingly short.

Given public:

$$
(N,e),
$$

do:

```text
1. compute continued fraction of e/N
2. enumerate convergents k/d
3. skip k = 0
4. require k | (ed - 1)
5. derive candidate phi
6. derive S = N - phi + 1
7. compute Δ = S² - 4N
8. require Δ to be a perfect square
9. reconstruct p and q
10. verify p*q = N
```

The first candidate that passes gives:

$$
d
$$

and usually the factors too.

This is not exponential search.

The continued fraction of a rational number is produced by Euclid in polynomial time in the bit length.

The number of convergents is small.

That is why Wiener's result is a **total polynomial-time break** for the vulnerable parameter region.

---

## 12. Python: continued fractions from scratch

Start with the same Euclidean divisions.

```python
def continued_fraction(numerator, denominator):
    terms = []

    while denominator:
        q = numerator // denominator
        terms.append(q)

        numerator, denominator = (
            denominator,
            numerator - q * denominator,
        )

    return terms
```

For:

```python
e = 17993
N = 90581
```

we get:

```text
[0, 5, 29, 4, 1, 3, 2, 4, 3]
```

Now generate convergents.

```python
def convergents(terms):
    h_prev2, h_prev1 = 0, 1
    k_prev2, k_prev1 = 1, 0

    for a in terms:
        h = a * h_prev1 + h_prev2
        k = a * k_prev1 + k_prev2

        yield h, k

        h_prev2, h_prev1 = h_prev1, h
        k_prev2, k_prev1 = k_prev1, k
```

The names:

```text
h = numerator
k = denominator
```

are conventional continued-fraction notation.

But once we enter the RSA attack I prefer to rename the candidate pair:

```text
candidate_k
candidate_d
```

because the numerator should correspond to the RSA integer $k$ and the denominator to the private exponent $d$.

---

## 13. Python: validate the RSA candidate

The key validation step is where many toy implementations become sloppy.

We should not test a candidate $d$ by decrypting one arbitrary message and declaring success.

Instead, reconstruct the RSA algebra.

```python
from math import isqrt


def validate_candidate(N, e, k, d):
    if k == 0:
        return None

    ed_minus_1 = e * d - 1

    if ed_minus_1 % k != 0:
        return None

    phi = ed_minus_1 // k

    S = N - phi + 1
    delta = S * S - 4 * N

    if delta < 0:
        return None

    root = isqrt(delta)

    if root * root != delta:
        return None

    if (S + root) % 2 != 0:
        return None

    p = (S + root) // 2
    q = (S - root) // 2

    if p * q != N:
        return None

    return p, q
```

This verifies the structural RSA relation itself.

Then:

```python
def wiener_attack(N, e):
    terms = continued_fraction(e, N)

    for candidate_k, candidate_d in convergents(terms):
        result = validate_candidate(
            N,
            e,
            candidate_k,
            candidate_d,
        )

        if result is not None:
            p, q = result
            return candidate_d, p, q

    return None
```

For our public key:

```text
N = 90581
e = 17993
```

the result is:

```text
d = 5
p = 379
q = 239
```

A complete private-key recovery from two public integers.

---

## 14. Print every convergent: cryptanalysis should be inspectable

For this project I do not want the demo to output only:

```text
private key found
```

I want the reader to see the search.

The demo prints a table like:

```text
index     k      d       candidate?
-----------------------------------
0         0      1       skip
1         1      5       VALID
2        29    146       no
3       117    589       no
...
```

At the successful line it then prints:

```text
candidate phi = 89964
S = p + q     = 618
delta         = 19600
sqrt(delta)   = 140
p             = 379
q             = 239
```

This is important.

The attack should not feel like:

```python
wiener_attack(pubkey)
```

and magic happens.

The public-key ratio generates rational approximations.

One approximation satisfies the RSA polynomial constraints.

That is the mechanism.

---

## 15. A failure experiment: normal-sized $d$

Now keep the same toy modulus:

$$
N=90{,}581,
$$

but choose a much more ordinary textbook exponent relation:

$$
e=65{,}537.
$$

Using the $\varphi(N)$ convention for this controlled experiment:

$$
d=e^{-1}\pmod{\varphi(N)}
$$

gives:

$$
d=26{,}801.
$$

Compare the Wiener scale.

For:

$$
N=90{,}581,
$$

we have approximately:

$$
\frac13N^{1/4}\approx5.78.
$$

The vulnerable example had:

$$
d=5.
$$

The comparison key has:

$$
d=26{,}801.
$$

That is nowhere near the Wiener region.

Run the exact same attack.

No convergent passes the RSA factor-validation test.

The function returns:

```text
None
```

This is an important experiment because it prevents the wrong conclusion:

> continued fractions break RSA.

They do not.

They break a highly abnormal parameter regime in which the private exponent is deliberately too small.

The parameter mistake creates the approximation.

Without that approximation, continued fractions have nothing special to lock onto.

---

## 16. Why a small private exponent was tempting

This attack makes more sense historically if we remember how modular exponentiation works.

A private RSA operation evaluates:

$$
c^d\bmod N.
$$

Square-and-multiply costs roughly:

$$
O(\log d)
$$

bit-level exponent steps.

So reducing the bit length of $d$ appears to reduce private-operation cost.

That was particularly attractive in devices with asymmetric computational resources.

But this is exactly the kind of optimization that cryptography punishes:

```text
performance shortcut
        ↓
new algebraic relation
        ↓
publicly observable approximation
        ↓
key recovery
```

Modern implementations instead obtain large speedups from CRT:

```text
mod N operation
      ↓
mod p + mod q
      ↓
CRT recombination
```

without intentionally shrinking the fundamental private exponent into Wiener's vulnerable range.

And CRT itself, as we already saw, has its own fault-attack surface.

There is rarely a free optimization in cryptography.

---

## 17. $\varphi(N)$ versus $\lambda(N)$: an important modern nuance

Earlier in the series we deliberately moved RSA key generation toward the PKCS #1 convention:

$$
ed\equiv1\pmod{\lambda(N)},
$$

where:

$$
\lambda(N)=\operatorname{lcm}(p-1,q-1).
$$

Wiener's classical derivation is normally written using:

$$
ed-k\varphi(N)=1.
$$

That is not a contradiction.

The original/classical attack is easiest to present in the textbook RSA setting where $d$ is chosen as an inverse modulo $\varphi(N)$.

Modern RSA standards describe valid private exponents using $\lambda(N)$.

The durable security lesson is not:

> "Switching from $\varphi$ to $\lambda$ fixes small-$d$ RSA."

It does not.

The durable lesson is:

> do not deliberately choose an abnormally small private exponent.

Standards-aware key generation places much stronger lower bounds on $d$ than Wiener's vulnerable $N^{1/4}$ scale.

For example, NIST FIPS 186-5 RSA signature-key generation requires:

$$
\boxed{
d>2^{\mathrm{nlen}/2},
}
$$

where `nlen` is the RSA modulus bit length.

For an `nlen`-bit modulus:

$$
N^{1/4}\approx2^{\mathrm{nlen}/4}.
$$

So the FIPS lower bound is vastly above the Wiener region.

That is not an accident.

Parameter-generation rules encode decades of cryptanalytic lessons.

---

## 18. Research history: Wiener is the beginning, not the end

Michael J. Wiener published:

**"Cryptanalysis of Short RSA Secret Exponents," IEEE Transactions on Information Theory 36(3), 1990, pp. 553–558.**

The attack showed that sufficiently short secret exponents can be recovered efficiently from the public key using continued fractions.

The paper's core insight is not merely:

```text
small d is bad
```

It is:

```text
RSA key equation
+
balanced primes
+
small d
=
excellent rational approximation
```

Later work pushed beyond the continued-fraction boundary.

Boneh and Durfee used lattice/small-root techniques to attack a larger asymptotic region, classically associated with:

$$
d<N^{0.292}.
$$

That does not make Wiener's attack obsolete.

It makes Wiener the conceptual entry point to a much deeper family:

```text
continued fractions
        ↓
small private exponent
        ↓
Diophantine approximation
        ↓
lattices
        ↓
Coppersmith
        ↓
Boneh–Durfee
```

This is why we are doing Wiener before Coppersmith.

It gives us the one-dimensional approximation intuition before moving into lattice geometry.

---

## 19. The exact theorem versus later refinements

There is a subtle research point worth recording.

Different summaries of Wiener's attack often quote slightly different numerical bounds around the:

$$
N^{1/4}
$$

scale.

A rigorous classical sufficient bound often used in teaching is:

$$
d<\frac13N^{1/4}
$$

under:

$$
q<p<2q.
$$

Later work has refined the sufficient boundary and analyzed generalized prime-balance conditions.

So I do not want to write:

> $N^{1/4}$ is a magical exact phase transition.

It is not.

The useful conceptual statement is:

> **private exponents around the quarter-power scale are structurally dangerous; the exact provable boundary depends on the theorem assumptions and refinement being used.**

That is a better research habit than memorizing one decimal constant without its hypotheses.

---

## 20. Tests are part of the attack explanation

The companion chapter contains:

```text
chapters/16_rsa_wiener_attack/
├── README.md
├── continued_fraction.py
├── attack.py
├── demo.py
└── test_attack.py
```

Run:

```powershell
python chapters/16_rsa_wiener_attack/demo.py
```

Then:

```powershell
pytest chapters/16_rsa_wiener_attack/test_attack.py -q
```

The tests verify:

1. continued-fraction expansion of $17993/90581$;
2. the convergent sequence;
3. exact recovery of $d=5$;
4. factor recovery:
   $$
   p=379,\qquad q=239;
   $$
5. reconstruction of:
   $$
   \varphi(N)=89964;
   $$
6. rejection of invalid convergents;
7. failure against the non-small-$d$ comparison key;
8. a real RSA encryption/decryption round-trip under the vulnerable key.

I want the last test because recovering numbers is not enough.

We should verify that the recovered private exponent actually inverts the RSA public operation.

---

## 21. What exactly broke?

Not RSA modular exponentiation.

Not integer factorization in general.

Not the public exponent.

Not CRT.

Not padding.

The broken assumption was:

```text
private exponent chosen abnormally small
```

which created:

$$
\frac{k}{d}
\approx
\frac{e}{N}
$$

with approximation quality strong enough for continued fractions to expose the secret denominator.

So our RSA attack map now contains:

```text
RSA
├── textbook structure
│   ├── determinism
│   └── malleability
│
├── bad/reused public-side parameters
│   ├── common modulus
│   └── Håstad broadcast
│
└── bad private-side parameters
    └── small d
        └── Wiener
            └── continued fractions
```

This is a qualitatively different attack family.

---

## 22. One final mental model

If I had to remember Wiener without code, I would remember this chain:

$$
ed-k\varphi(N)=1
$$

means:

$$
\frac{k}{d}
\approx
\frac{e}{\varphi(N)}.
$$

Balanced primes mean:

$$
\varphi(N)\approx N.
$$

So:

$$
\frac{k}{d}
\approx
\frac{e}{N}.
$$

If $d$ is tiny enough, the approximation is so good that:

$$
\frac{k}{d}
$$

must be a continued-fraction convergent of:

$$
\frac{e}{N}.
$$

Enumerate convergents.

Recover $d$.

Validate via:

$$
\varphi(N)
\rightarrow
p+q
\rightarrow
x^2-(p+q)x+N
\rightarrow
p,q.
$$

That is the complete cryptanalytic story.

And it began with Euclidean division.

---

The next step should **not** jump immediately into Boneh–Durfee code.

That would hide too much machinery.

Before we can understand why a lattice pushes the small-$d$ boundary beyond Wiener, we need to build the mathematical object that makes Coppersmith possible.

So the next RSA deep dive will introduce the attack framework rather than treating LLL as a magic function:

**Next RSA Deep Dive:** *Coppersmith From Zero — How a Small Modular Root Becomes an Integer Polynomial Problem.*

That will give us the bridge:

```text
polynomials
→ modular roots
→ coefficient lattices
→ LLL
→ Coppersmith
→ Boneh–Durfee / short-pad / partial-key attacks
```
