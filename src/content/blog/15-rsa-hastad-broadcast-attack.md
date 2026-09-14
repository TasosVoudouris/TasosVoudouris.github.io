---
title: 'RSA Deep Dive III: Håstad''s Broadcast Attack'
description: When the same unrandomized RSA message is sent to several recipients with a small public exponent, CRT can reconstruct the message's exact integer power—and an ordinary integer root reveals the plaintext.
pubDate: '2026-09-09'
topics:
- Public-Key Cryptography
- Cryptanalysis
- Number Theory
tags:
- rsa
- hastad
- broadcast-attack
- crt
- low-public-exponent
- cryptanalysis
- cryptography-from-zero
difficulty: Intermediate
series: RSA Deep Dives
seriesOrder: 3
draft: false
---
The previous RSA Deep Dive used Bézout coefficients to combine two ciphertexts.

This one uses a different piece of mathematics we have already built:

**the Chinese Remainder Theorem.**

The setup also changes in a very precise way.

In the common-modulus attack we had:

```text
same modulus
same message
different public exponents
```

Now we will have:

```text
different moduli
same message
same small public exponent
```

and the attack becomes:

```text
collect ciphertexts
        ↓
CRT reconstruction
        ↓
recover the exact integer m^e
        ↓
take an ordinary integer e-th root
        ↓
recover m
```

No factorization.

No private exponent.

No decryption oracle.

The attack works because textbook RSA exposes the same low-degree algebraic relation to several independent recipients.

If you want to refresh the prerequisites first:

- [The Chinese Remainder Theorem](/blog/10-chinese-remainder-theorem/)
- [RSA Key Generation From Zero](/blog/12-rsa-key-generation/)
- [RSA Deep Dive I: Why Textbook RSA Fails](/blog/13-rsa-deep-dive-textbook-rsa-fails/)
- [RSA Deep Dive II: The Common-Modulus Attack](/blog/14-rsa-common-modulus-attack/)

![Håstad broadcast attack: CRT reconstructs the exact cube](/images/blog/15-rsa-hastad-broadcast.svg)

*Each ciphertext reveals the same integer cube modulo a different RSA modulus. CRT stitches the residues together; once the product of the moduli is larger than the cube, modular ambiguity disappears.*

---

## 1. Start with the simpler low-exponent mistake

Before the broadcast attack, there is an even simpler failure worth understanding.

Suppose textbook RSA uses:

$$
e=3
$$

and encrypts:

$$
c=m^3\bmod N.
$$

If the message is so small that:

$$
m^3<N,
$$

then modular reduction never happens.

So:

$$
c=m^3
$$

as an ordinary integer.

The attacker can simply compute:

$$
m=\sqrt[3]{c}.
$$

That is not really an attack on RSA's hidden factorization.

The RSA modulus was never used in a meaningful way.

The exponentiation stayed below it.

For example, if:

$$
m=10
$$

and:

$$
N>1000,
$$

then:

$$
c=10^3\bmod N=1000.
$$

Take the integer cube root:

$$
\sqrt[3]{1000}=10.
$$

Done.

Secure randomized encoding prevents application messages from becoming tiny, predictable raw RSA integers.

But Håstad's broadcast attack is more interesting because it can work even when **every individual ciphertext has wrapped around its own modulus**.

That is the part I want to derive carefully.

---

## 2. The broadcast setup

Suppose Alice wants to send the same plaintext representative:

$$
m
$$

to three different recipients.

Each recipient has an independently generated RSA key:

$$
(N_1,e),
\qquad
(N_2,e),
\qquad
(N_3,e).
$$

Assume the public exponent is the small value:

$$
e=3.
$$

Alice performs raw textbook RSA independently:

$$
c_1\equiv m^3\pmod{N_1},
$$

$$
c_2\equiv m^3\pmod{N_2},
$$

$$
c_3\equiv m^3\pmod{N_3}.
$$

An eavesdropper sees:

$$
(N_1,c_1),
\qquad
(N_2,c_2),
\qquad
(N_3,c_3).
$$

The attacker does not know the prime factors of any modulus.

But notice what the three ciphertexts really are.

They are three modular views of the **same hidden integer**:

$$
m^3.
$$

That sentence is the bridge to CRT.

---

### The assumptions

For the clean textbook form of the attack, assume:

1. the same raw representative $m$ is used for every recipient;
2. the exponent is the same small $e=3$;
3. the moduli are pairwise coprime:
   $$
   \gcd(N_i,N_j)=1
   \quad
   \text{for }i\ne j;
   $$
4. the combined modulus product is larger than the integer power:
   $$
   m^3<N_1N_2N_3.
   $$

Under those conditions, the plaintext can be recovered efficiently.

The fourth condition is the one that makes the attack almost feel like a magic trick.

It is not magic.

It follows directly from uniqueness in CRT.

---

## 3. Why CRT gives the *integer* cube, not only a residue

CRT tells us that there exists a unique value:

$$
C
$$

with:

$$
0\le C<N_1N_2N_3
$$

such that:

$$
C\equiv c_1\pmod{N_1},
$$

$$
C\equiv c_2\pmod{N_2},
$$

$$
C\equiv c_3\pmod{N_3}.
$$

But each ciphertext satisfies:

$$
c_i\equiv m^3\pmod{N_i}.
$$

Therefore $m^3$ satisfies exactly the same congruence system:

$$
m^3\equiv c_i\pmod{N_i}.
$$

Now suppose:

$$
m^3<N_1N_2N_3.
$$

Then both:

$$
C
$$

and:

$$
m^3
$$

lie inside the CRT uniqueness interval:

$$
[0,N_1N_2N_3).
$$

They satisfy the same residues.

There can be only one such representative.

Therefore:

$$
\boxed{C=m^3}
$$

as an **ordinary integer equality**.

That is the key moment.

We have moved from:

$$
m^3\bmod N_1,
\quad
m^3\bmod N_2,
\quad
m^3\bmod N_3
$$

back to:

$$
m^3\in\mathbb Z.
$$

Once that happens, RSA has disappeared from the problem.

We take:

$$
\boxed{m=\sqrt[3]{C}}.
$$

---

## 4. A complete toy attack where every individual ciphertext wraps

I want an example where the attack cannot be dismissed as:

> "The message cube was already smaller than one modulus."

So choose:

$$
m=100.
$$

Then:

$$
m^3=1{,}000{,}000.
$$

Now choose three independently factored toy RSA moduli:

$$
N_1=11\cdot17=187,
$$

$$
N_2=23\cdot29=667,
$$

$$
N_3=41\cdot47=1927.
$$

For each modulus, $e=3$ is a valid toy public exponent because it is coprime to the corresponding Carmichael value.

The important inequalities are:

$$
1{,}000{,}000>187,
$$

$$
1{,}000{,}000>667,
$$

$$
1{,}000{,}000>1927.
$$

So every individual encryption really performs modular reduction.

No single ciphertext is the integer cube.

Compute the ciphertexts:

$$
c_1
=
100^3\bmod187
=
111,
$$

$$
c_2
=
100^3\bmod667
=
167,
$$

$$
c_3
=
100^3\bmod1927
=
1814.
$$

The attacker sees only:

```text
(N1, c1) = (187, 111)
(N2, c2) = (667, 167)
(N3, c3) = (1927, 1814)
e = 3
```

Now check pairwise coprimality:

$$
\gcd(187,667)=1,
$$

$$
\gcd(187,1927)=1,
$$

$$
\gcd(667,1927)=1.
$$

So CRT applies.

The product is:

$$
P
=
187\cdot667\cdot1927
=
240{,}352{,}783.
$$

And:

$$
m^3
=
1{,}000{,}000
<
240{,}352{,}783.
$$

So the uniqueness condition is satisfied.

Now let us perform the CRT construction rather than calling it a black box.

Set:

$$
P_1=\frac{P}{187}=1{,}285{,}309,
$$

$$
P_2=\frac{P}{667}=360{,}349,
$$

$$
P_3=\frac{P}{1927}=124{,}729.
$$

We need inverses:

$$
y_1=P_1^{-1}\pmod{187}=158,
$$

$$
y_2=P_2^{-1}\pmod{667}=371,
$$

$$
y_3=P_3^{-1}\pmod{1927}=1154.
$$

The constructive CRT solution is:

$$
C
\equiv
c_1P_1y_1
+
c_2P_2y_2
+
c_3P_3y_3
\pmod P.
$$

Substitute:

$$
C
\equiv
111(1{,}285{,}309)(158)
+
167(360{,}349)(371)
+
1814(124{,}729)(1154)
\pmod{240{,}352{,}783}.
$$

Reducing the sum modulo $P$ gives:

$$
\boxed{C=1{,}000{,}000}.
$$

Now compute the exact integer cube root:

$$
\sqrt[3]{1{,}000{,}000}=100.
$$

Therefore:

$$
\boxed{m=100}.
$$

No RSA modulus was factored.

No private exponent was recovered.

The attacker recovered the plaintext by reconstructing the same low-degree integer relation across recipients.

---

## 5. The Python implementation should mirror the proof

The attack needs only three mathematical components:

```text
pairwise-GCD checks
CRT
exact integer e-th root
```

Here is the shape of the implementation:

```python
def hastad_broadcast(ciphertexts, moduli, exponent):
    C, modulus_product = crt(ciphertexts, moduli)

    root, exact = integer_nth_root(C, exponent)

    if not exact:
        raise ValueError(
            "CRT result is not an exact e-th power"
        )

    return root
```

But I do not want `crt()` and `integer_nth_root()` to remain invisible helpers.

The companion chapter implements both from scratch.

For CRT:

```python
def crt(residues, moduli):
    P = math.prod(moduli)
    result = 0

    for residue, modulus in zip(residues, moduli):
        partial = P // modulus
        inverse = pow(partial, -1, modulus)

        result += residue * partial * inverse

    return result % P, P
```

And for the exact integer root we use binary search rather than floating point.

That distinction matters.

For cryptographic-size integers, this is dangerous:

```python
round(C ** (1 / 3))
```

because floating-point arithmetic cannot represent arbitrary large integers exactly.

We want integer arithmetic all the way down.

A simple exact root routine is:

```python
def integer_nth_root(value, n):
    low = 0
    high = 1

    while high**n <= value:
        high *= 2

    while low + 1 < high:
        mid = (low + high) // 2

        if mid**n <= value:
            low = mid
        else:
            high = mid

    return low, low**n == value
```

The boolean is important.

We are not merely asking for:

```text
floor(cuberoot(C))
```

We want to know whether:

$$
C
$$

is **exactly** an $e$-th power.

For the attack:

```text
C = 1000000
root = 100
exact = True
```

That exactness check is one of the cleanest ways to detect whether the simple broadcast assumptions held.

---

## 6. Why three recipients for e = 3?

The famous textbook statement is often:

> with public exponent $e=3$, three ciphertexts are enough.

The general sufficient argument is straightforward.

Suppose the same message satisfies:

$$
m<N_i
$$

for every recipient.

With $e$ pairwise-coprime moduli:

$$
N_1,\ldots,N_e,
$$

we have:

$$
m^e
<
N_1N_2\cdots N_e.
$$

Why?

Because:

$$
m<N_i
$$

for every $i$, so multiplying all $e$ inequalities gives:

$$
m^e<\prod_{i=1}^{e}N_i.
$$

Therefore $e$ recipients are sufficient for the basic same-message attack.

For:

$$
e=3,
$$

three recipients guarantee the bound.

But there is an important nuance:

> $e$ ciphertexts are sufficient, not always necessary.

If the message is unusually small, even fewer moduli may already have a product larger than $m^e$.

The real condition is:

$$
\boxed{
m^e<\prod_i N_i.
}
$$

The recipient count is just a convenient way to guarantee it under the usual $m<N_i$ assumption.

---

## 7. A failure experiment: two ciphertexts are not enough here

For our chosen example:

$$
m=100.
$$

Using only the first two moduli:

$$
N_1N_2
=
187\cdot667
=
124{,}729.
$$

But:

$$
m^3
=
1{,}000{,}000
>
124{,}729.
$$

So CRT with only two ciphertexts cannot return the exact cube.

It reconstructs:

$$
C_{12}
=
m^3\bmod(N_1N_2).
$$

Numerically:

$$
C_{12}=2168.
$$

And:

$$
12^3=1728,
$$

$$
13^3=2197.
$$

So $2168$ is not an exact cube.

Our implementation should reject the simple attack:

```text
CRT reconstruction = 2168
exact cube? False
```

That is important pedagogically.

I do not want attack code that simply prints a plausible integer and declares victory.

A good cryptanalytic implementation should verify its own assumptions.

---

## 8. What if the RSA moduli are not pairwise coprime?

CRT in this clean form assumes:

$$
\gcd(N_i,N_j)=1.
$$

But suppose two recipients accidentally share a prime factor.

For example:

$$
N_1=pq_1,
$$

$$
N_2=pq_2.
$$

Then:

$$
\gcd(N_1,N_2)=p.
$$

The attacker has something even better than the broadcast attack:

**a factor of both RSA moduli.**

So our code checks pairwise GCDs before doing CRT.

If it finds:

$$
1<\gcd(N_i,N_j)<N_i,
$$

that is not merely:

```text
CRT cannot continue
```

It is:

```text
RSA key-generation failure detected
```

This connects directly back to the shared-prime story from Blog 01.

Again, the same GCD routine keeps reappearing in completely different parts of cryptography.

---

## 9. This is the simple broadcast attack—not the full Håstad theorem

There is a historical nuance I want to keep because this is a **Deep Dive**, not a flashcard.

The attack we just implemented is the classic simple broadcast scenario:

$$
c_i\equiv m^e\pmod{N_i}.
$$

CRT recovers $m^e$ once the combined range is large enough.

But Håstad's 1988 result is broader.

His paper studies simultaneous low-degree modular equations:

$$
P_i(x)\equiv0\pmod{N_i},
$$

where the $P_i$ are low-degree polynomials.

That means simple deterministic padding or recipient-specific linear transformations do not necessarily save low-exponent RSA.

The paper proves polynomial-time recovery results for sufficiently many relatively prime moduli under specific degree/size conditions.

So the important historical lesson is not merely:

> "Never send exactly the same integer three times with $e=3$."

It is broader:

> predictable low-degree algebraic relations across many low-exponent RSA instances can be dangerous.

The full result uses lattice machinery.

We are **not** deriving that machinery yet.

That belongs later when we build:

- lattices,
- LLL,
- Coppersmith small roots,
- Franklin-Reiter related-message attacks.

But I want the reader to know where this simple CRT attack sits in the larger cryptanalytic landscape.

**Primary reference:** Johan Håstad, *Solving Simultaneous Modular Equations of Low Degree*, SIAM Journal on Computing 17(2), 1988, pp. 336–341.

---

## 10. What actually caused the failure?

It is tempting to conclude:

```text
e = 3 is broken
```

That is too crude.

The actual failure is a composition:

```text
small public exponent
        +
same / algebraically related plaintext representative
        +
textbook deterministic RSA
        +
enough independent moduli
        =
reconstructable low-degree integer relation
```

Take away the repeated raw representative and the simple proof collapses.

That is why secure RSA encryption uses randomized encoding.

With RSAES-OAEP:

```text
same application message M
        ↓ fresh seed 1
encoded representative EM1

same application message M
        ↓ fresh seed 2
encoded representative EM2

same application message M
        ↓ fresh seed 3
encoded representative EM3
```

Normally:

$$
EM_1\ne EM_2\ne EM_3.
$$

The attacker no longer has:

$$
c_i\equiv m^3\pmod{N_i}
$$

for one common unknown $m$.

Instead:

$$
c_i\equiv EM_i^e\pmod{N_i}
$$

with different randomized representatives.

There is no single cube for CRT to reconstruct.

That is the structural defense.

---

### What about using $e=65537$?

Modern RSA commonly uses:

$$
e=65537.
$$

This also makes the naive broadcast arithmetic completely different: the sufficient recipient count for the direct same-message argument would be enormous.

But the lesson from Deep Dive I still applies.

A large or conventional exponent does **not** turn raw textbook RSA into a secure encryption scheme.

Textbook RSA remains deterministic.

It remains algebraically structured.

The correct defense is not:

```text
replace 3 with 65537 and keep raw RSA
```

It is:

```text
use a standardized randomized encryption scheme
```

such as RSAES-OAEP where RSA encryption is still required for compatibility.

That distinction matters.

---

## 11. Compare the first three RSA Deep Dives

We can now see three RSA failures side by side.

### Deep Dive I — raw RSA algebra

Given:

$$
c=m^e\bmod N,
$$

determinism leaks equality and multiplicativity enables ciphertext malleability.

Tool:

```text
RSA algebra itself
```

### Deep Dive II — common modulus

Given:

$$
c_1=m^{e_1}\bmod N,
$$

$$
c_2=m^{e_2}\bmod N,
$$

with:

$$
\gcd(e_1,e_2)=1,
$$

Bézout synthesizes exponent $1$.

Tool:

```text
Extended Euclid
```

### Deep Dive III — broadcast attack

Given:

$$
c_i=m^e\bmod N_i,
$$

for enough pairwise-coprime moduli, CRT reconstructs the exact integer $m^e$.

Tool:

```text
CRT + integer root
```

So our attack graph is becoming:

```text
                     textbook RSA
                          |
         +----------------+----------------+
         |                                 |
   algebraic structure              parameter/message reuse
         |                                 |
 determinism / CCA                 +--------+---------+
                                   |                  |
                             common modulus       broadcast
                                   |                  |
                                Bézout               CRT
```

This is much more useful than memorizing attack names.

Each attack has a recognizable structural trigger.

---

## 12. Run the full experiment

The companion chapter now contains:

```text
chapters/15_rsa_hastad_broadcast/
├── README.md
├── attack.py
├── demo.py
└── test_attack.py
```

Run:

```powershell
python chapters/15_rsa_hastad_broadcast/demo.py
```

Then:

```powershell
pytest chapters/15_rsa_hastad_broadcast/test_attack.py -q
```

The demo performs four stages:

```text
1. generate the three toy ciphertexts
2. show that every individual ciphertext wrapped modulo Ni
3. reconstruct m^3 with CRT
4. take and verify the exact cube root
```

Then it intentionally removes one ciphertext and demonstrates:

```text
simple broadcast recovery fails
```

because the CRT range is too small.

Finally, the tests check:

- exact CRT reconstruction,
- exact integer-root logic,
- successful broadcast recovery,
- failure with insufficient data,
- rejection of non-coprime moduli.

The code is not an appendix to the mathematics.

It is the mathematics made executable.

---

## 13. What I want to remember from this attack

If I had to compress the whole post into one idea, it would be this:

> Modular reduction hides an integer only inside one modulus. Several compatible modular views can remove that ambiguity.

In Håstad's broadcast setting:

$$
m^e
$$

is hidden separately behind:

$$
\bmod N_1,
\quad
\bmod N_2,
\quad
\bmod N_3.
$$

CRT increases the observable range from each individual $N_i$ to:

$$
N_1N_2N_3.
$$

Once that range becomes larger than the hidden integer power:

$$
m^e,
$$

the wrap-around ambiguity disappears.

Then an integer root finishes the job.

That is why this attack is such a good continuation of the CRT post.

CRT is not "an RSA optimization theorem."

It is a reconstruction theorem.

Whether that reconstruction helps the defender or the attacker depends entirely on what modular information is available.

---

The next RSA attack changes direction again.

So far our public exponent has been the dangerous parameter.

Next we make the **private exponent** too small.

Then a relation of the form:

$$
ed-k\varphi(N)=1
$$

will imply that:

$$
\frac{k}{d}
$$

is an unusually good rational approximation to:

$$
\frac{e}{N}.
$$

And continued fractions can recover it.

That brings another apparently pure mathematical topic directly into cryptanalysis.

**Next RSA Deep Dive:** *Wiener's Attack From Zero: How Continued Fractions Recover a Small RSA Private Exponent.*
