# RSA Deep Dive II — Common-Modulus Attack Cross-Check

## Goal

Second post in the RSA topic-closing Deep Dive block.

Primary connection:

```text
Blog 02 Extended Euclid / Bezout
        ↓
RSA public exponents
        ↓
common-modulus plaintext recovery
```

This post should make an "easy" mathematical topic visibly reappear as
intermediate cryptanalysis.

---

## Sources compared

### Older user material

A previous RSA lecture already contains a three-part Common Modulus Attack
derivation.

It correctly states:

```text
c1 = M^e1 mod n
c2 = M^e2 mod n
gcd(e1,e2) = 1
```

and uses Extended Euclid to find:

```text
x*e1 + y*e2 = 1.
```

Then:

```text
c1^x * c2^y = M mod n.
```

It also correctly handles negative exponents through modular inverses and states
the invertibility condition.

The public Deep Dive retains this core mechanism.

---

## Mature lesson example retained

The newer `Cryptography I · Lesson 09` contains the checked example:

```text
N  = 77
m  = 9
e1 = 7
e2 = 11

c1 = 37
c2 = 53
```

and:

```text
8*7 - 5*11 = 1.
```

Therefore:

```text
37^8 * 53^(-5) = 9 mod 77.
```

This exact example is retained.

Additional checked intermediates:

```text
53^(-1) mod 77 = 16
37^8 mod 77    = 53
16^5 mod 77    = 67
53*67 mod 77   = 9
```

---

## Old-story correction

The old slide described the second encryption as arising from an error such as:

```text
CPU overheating or bit flipping
```

that somehow changes the public exponent.

That story is not retained.

It mixes a parameter-reuse design problem with a hardware fault scenario.

The public article instead gives the clean structural condition:

```text
same modulus
same textbook representative
different public exponents
```

This is more accurate and easier to reason about.

---

## Conditions stated precisely

The simple attack requires:

1. same modulus `N`;
2. same underlying textbook RSA representative `m`;
3. `gcd(e1,e2)=1`;
4. any ciphertext raised to a negative Bezout coefficient must be invertible
   modulo `N`.

If the required ciphertext is not invertible and its GCD with `N` is
non-trivial, that GCD itself factors the modulus.

---

## gcd(e1,e2) > 1 nuance

The article does NOT say that the attack "works the same" when the public
exponents are not coprime.

If:

```text
g = gcd(e1,e2) > 1
```

Bezout gives:

```text
a*e1 + b*e2 = g
```

and the direct combination yields:

```text
m^g mod N
```

rather than `m`.

Further exploitation depends on additional structure and is deliberately not
collapsed into the simple attack.

---

## Two meanings of "common modulus attack"

A useful correction was added.

### Passive same-message exponent-combination attack

This post's main subject:

```text
same N
same m
coprime e1,e2
public ciphertexts
-> Bezout
-> recover m
```

### Shared-modulus-across-users private-key failure

Boneh's 1999 RSA attack survey discusses an even more fundamental shared-modulus
design where multiple users receive distinct valid `(e_i,d_i)` pairs for one
common `N`.

Knowledge of a valid private exponent for that shared modulus can be used to
attack the factorization of `N`, compromising the other users.

The article distinguishes these instead of treating every shared-modulus issue
as one identical attack.

Reference:

Dan Boneh,
"Twenty Years of Attacks on the RSA Cryptosystem,"
Notices of the AMS, 46(2), 1999, pp. 203-213.

---

## Mature CryptoBible framing

The current mature RSA attack map classifies:

```text
common modulus
Hastad broadcast
low-exponent cases
```

under:

```text
bad / reused parameters
```

rather than generic factorization.

It also explicitly gives the same Bezout formula and notes that RSA moduli
should be independently generated rather than treated like Diffie-Hellman domain
parameters.

That framing is preserved.

---

## OAEP connection

The article explains that randomized encoding changes the same application
message into independently randomized encoded representatives.

Thus normal RSAES-OAEP use removes the exact:

```text
same raw m under e1 and e2
```

structure required by this toy attack.

However, OAEP is not presented as a justification for shared RSA moduli.

Independent key generation remains the structural mitigation.

---

## Current Cryptography From Zero code audit

Current `v1.4` RSA attack code contains:

- tiny-modulus trial factoring;
- deterministic textbook RSA check;
- Bellcore CRT fault recovery.

It does not yet contain the common-modulus attack.

Therefore this package adds a standalone new chapter:

```text
repo/chapters/14_rsa_common_modulus/demo.py
```

for later integration into the main project.

The demo implements:

- `xgcd`;
- signed modular exponentiation;
- common-modulus recovery;
- a non-coprime-exponent checkpoint.

---

## Safety / scope

The demo uses only the fixed toy modulus:

```text
N = 77.
```

It is an educational local arithmetic demonstration.

No network interaction, scanning, key collection, or real-world target logic is
included.

---

## Next RSA Deep Dive

Recommended:

```text
RSA Deep Dive III
Hastad's Broadcast Attack:
same small exponent
same plaintext
different pairwise-coprime moduli
-> CRT
-> integer root
```

This deliberately reconnects Blog 10 (CRT) to RSA cryptanalysis.

---

## Publication checklist

Verify:

- Is the same-modulus setup unambiguous?
- Is the same-message requirement explicit?
- Can the reader derive `8*7 - 5*11 = 1`?
- Is the negative exponent explained as a modular inverse?
- Does the reader understand why invertibility matters?
- Is the `gcd(e1,e2)>1` case not oversimplified?
- Are the two shared-modulus failure modes distinguished?
- Is the old hardware-fault story removed?
- Does the mitigation emphasize independent RSA moduli?
- Does the next Håstad/CRT transition feel natural?

Any "no" means another revision.


## Bézout coefficient non-uniqueness

The first implementation check returned:

```text
-3*7 + 2*11 = 1
```

while the mature lesson uses:

```text
8*7 - 5*11 = 1.
```

Both are valid.

General solutions are:

```text
a = a0 + k*e2
b = b0 - k*e1.
```

With `(a0,b0)=(-3,2)` and `k=1`, this gives `(8,-5)`.

The companion demo now makes this explicit rather than assuming Extended Euclid
must return one particular coefficient pair.
