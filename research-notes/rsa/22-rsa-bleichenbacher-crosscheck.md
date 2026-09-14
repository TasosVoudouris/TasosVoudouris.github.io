# RSA Deep Dive X — Bleichenbacher Cross-Check

## Scope

This package is site-first and scientific.

It studies the mathematical core of Bleichenbacher's adaptive chosen-ciphertext
result through a deliberately idealized interval predicate.

It does not implement:

- a real PKCS #1 v1.5 protocol client;
- network interaction;
- endpoint probing;
- automatic oracle discovery;
- adaptive multiplier-search logic against deployed systems.

The fixed experiment verifies only the interval arithmetic.

---

## Existing user-material cross-check

The mature RSA material already classifies:

```text
Padding / validity oracle
-> receiver reveals information about decoded plaintext structure
-> Bleichenbacher; Manger
```

and explicitly states:

```text
decryption errors are part of the attack surface.
```

It also warns that RSAES-PKCS1-v1_5 decoding failures must not become
externally distinguishable.

That framing is preserved.

---

## Standards cross-check

RFC 8017 specifies RSAES-PKCS1-v1_5 encoded blocks as:

```text
EM = 0x00 || 0x02 || PS || 0x00 || M
```

where:

- `PS` consists of pseudorandom nonzero octets;
- `PS` is at least eight octets long.

The decoder checks:

- first octet is `0x00`;
- second octet is `0x02`;
- a zero separator exists;
- the padding string is at least eight octets.

RFC 8017 also explicitly warns that implementations must prevent an opponent
from distinguishing decoding errors.

---

## Primary historical reference

Daniel Bleichenbacher:

```text
Chosen Ciphertext Attacks Against Protocols
Based on the RSA Encryption Standard PKCS #1
CRYPTO '98
LNCS 1462
pp. 1-12
DOI 10.1007/BFb0055716
```

The public article presents only the interval mechanism, not an operational
reproduction of the original attack workflow.

---

## Interval model

For a `k`-octet modulus define:

```text
B = 2^(8(k-2)).
```

Any encoded integer starting with bytes:

```text
00 02
```

satisfies:

```text
2B <= m <= 3B-1.
```

The companion therefore defines the idealized predicate:

```text
O(c) = 1 iff RSA-decrypted representative is in [2B,3B-1].
```

This is intentionally weaker/simpler than a full PKCS #1 v1.5 conformance
oracle.

The distinction is explicit in the public article.

---

## Multiplicative transformation

For:

```text
c = m^e mod N
```

and fixed multiplier `s`:

```text
c' = c * s^e mod N
```

decrypts to:

```text
m' = m*s mod N.
```

A positive predicate implies there exists an integer `r` such that:

```text
2B <= m*s - r*N <= 3B-1.
```

Therefore:

```text
ceil((2B+rN)/s)
<= m <=
floor((3B-1+rN)/s).
```

If the current candidate interval is `[a,b]`, compatible wrap integers satisfy:

```text
ceil((a*s-(3B-1))/N)
<= r <=
floor((b*s-2B)/N).
```

These are the exact update equations checked by the companion.

---

## Fixed toy values

```text
p = 60013
q = 61027
N = 3662413351
e = 17
m = 150000
```

The modulus has:

```text
k = 4 octets.
```

Therefore:

```text
B = 65536
2B = 131072
3B-1 = 196607.
```

Initial candidate set:

```text
[131072, 196607]
```

contains 65536 integers.

### First fixed positive multiplier

```text
s1 = 24417
```

For the hidden toy value:

```text
m*s1 mod N = 136649
```

which is inside the interval.

The corresponding modular wrap is:

```text
r = 1.
```

Interval update gives:

```text
[150000, 150002].
```

### Second fixed positive multiplier

```text
s2 = 195330
```

For the hidden value:

```text
m*s2 mod N = 193192
```

with:

```text
r = 8.
```

Intersecting the resulting interval with the previous candidate set gives:

```text
[150000,150000].
```

Thus the fixed model demonstrates:

```text
65536 candidates
-> 3 candidates
-> 1 candidate.
```

The article explicitly states that this dramatic reduction is an artifact of
tiny pedagogical parameters and is not a query-complexity model for real RSA.

---

## Adaptive terminology

The article defines "adaptive" precisely:

```text
the next chosen transformation may depend on previous oracle responses.
```

The companion itself does not implement adaptive search.

It uses two preselected positive multipliers solely to verify the interval
update mathematics.

---

## Manger connection

The article mentions Manger only as the next conceptual step.

The existing mature RSA material correctly notes that Manger's 2001 result
studies an OAEP implementation exposing a suitable validity distinction.

That deserves a separate post because the numerical predicate differs from the
PKCS #1 v1.5 interval used here.

---

## Publication checklist

Verify:

- Is the PKCS #1 v1.5 block structure stated correctly?
- Is full conformance distinguished from the simplified prefix interval?
- Is `B=2^(8(k-2))` derived?
- Is `[2B,3B-1]` explicit?
- Is the oracle framed as a predicate rather than plaintext disclosure?
- Is RSA multiplicativity derived?
- Is the wrap integer `r` introduced clearly?
- Is the interval formula derived line by line?
- Is the compatible `r` range derived from `[a,b]`?
- Are the fixed toy values reproducible?
- Does the first predicate reduce the interval to `[150000,150002]`?
- Does the second reduce it to one value?
- Is the toy reduction explicitly not presented as realistic query complexity?
- Is adaptivity defined?
- Is the implementation/error-behavior lesson explicit?
- Is the next Manger transition natural?

Any "no" means another revision.
