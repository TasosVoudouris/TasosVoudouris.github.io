# RSA Deep Dive XI — Manger Cross-Check

## Scope

This is a site-first scientific treatment.

The companion script runs only on one fixed toy RSA modulus and models the
idealized predicate:

```text
m*f mod N < B
```

It does not include:

- network interaction;
- OAEP endpoint probing;
- oracle discovery;
- timing measurement;
- a reusable target interface.

Its purpose is to verify Manger's interval mathematics.

## Existing user-material cross-check

The mature CryptoBible material already states:

```text
Manger later demonstrated an adaptive chosen-ciphertext attack
against RSA-OAEP implementations when the receiver exposed
a suitable validity distinction.
```

It also preserves the correct security lesson:

```text
do not expose internal OAEP failure distinctions by message,
timing, or other partial information.
```

The current article expands exactly that statement.

## RFC 8017 cross-check

Current RSAES-OAEP uses:

```text
EM = Y || maskedSeed || maskedDB
```

with:

```text
Y = 0x00.
```

RFC 8017's OAEP decryption specifies the single public error:

```text
"decryption error"
```

and explicitly warns that an opponent must not distinguish internal OAEP
error conditions by error message, timing, or other partial information about
`EM`.

The RFC cites Manger for this chosen-ciphertext issue.

## Primary paper

James Manger:

```text
A Chosen Ciphertext Attack on RSA Optimal
Asymmetric Encryption Padding (OAEP)
as Standardized in PKCS #1 v2.0

CRYPTO 2001
LNCS 2139
pp. 230-238
DOI 10.1007/3-540-44647-8_14
```

The paper defines:

```text
B = 2^(8(k-1))
```

and assumes the oracle distinguishes:

```text
m < B
```

from:

```text
m >= B.
```

It assumes `2B < N` for the clean three-phase presentation.

## Three-phase structure preserved

### Step 1

Try:

```text
2, 4, 8, ...
```

until the oracle returns `>= B`.

This identifies a known multiple for which the hidden plaintext is bounded
between one-half and one full `B` interval.

### Step 2

Start from a multiple based on:

```text
floor((N+B)/B)
```

times the step-1 half multiplier.

Increase by the half multiplier until the oracle returns `< B`.

The successful value satisfies:

```text
N <= f2*m < N+B.
```

### Step 3

Maintain one interval:

```text
[mmin,mmax]
```

and choose a multiplier whose transformed interval spans approximately `2B`
around one boundary:

```text
i*N + B.
```

Both oracle responses narrow the range.

## Fixed toy model

```text
p = 60013
q = 61027
N = 3662413351
e = 17
d = 3231434393
```

Four-octet modulus:

```text
k = 4
B = 2^24 = 16777216
```

Hidden representative:

```text
m = 12345678 < B.
```

Target ciphertext:

```text
c = 48744796.
```

### Phase 1

```text
f1 = 2
2*m = 24691356 >= B.
```

Thus the phase-1 half multiplier is `1`, giving:

```text
B/2 <= m < B.
```

### Phase 2

Initial candidate:

```text
f2 = floor((N+B)/B) = 219.
```

The first `< B` result occurs at:

```text
f2 = 297.
```

Then:

```text
297*m - N = 4253015 < B
```

so:

```text
N <= 297*m < N+B.
```

This yields:

```text
m in [12331359,12387847].
```

### Phase 3

The fixed implementation applies the paper's interval construction.

First two updates:

```text
f3=594, oracle < B
[12331359,12387847]
-> [12331359,12359602]

f3=1188, oracle >= B
-> [12345481,12359602].
```

After fifteen phase-3 updates:

```text
[12345678,12345678].
```

The exact hidden toy representative is recovered.

## Complexity wording

The public article reports Manger's own historical estimates:

```text
~1100 queries for 1024-bit RSA
~2200 queries for 2048-bit RSA
```

as analytical figures from the 2001 paper.

They are not presented as measurements of current software.

## OAEP security wording

The article does NOT state:

```text
OAEP is mathematically broken.
```

It states:

```text
an OAEP implementation that leaks the relevant internal boundary
can create an adaptive chosen-ciphertext oracle.
```

This is consistent with both the Manger paper and RFC 8017.

## Publication checklist

Verify:

- Is `B=2^(8(k-1))` distinguished from Bleichenbacher's `B`?
- Is OAEP's leading zero octet connected to `m<B`?
- Is the oracle described numerically?
- Is RSA multiplicativity derived?
- Is the `2B<N` assumption explicit?
- Are all three phases explained?
- Does phase 1 locate the scale of `m`?
- Does phase 2 establish `N <= f2*m < N+B`?
- Does phase 3 explain the boundary `iN+B`?
- Are both oracle outcomes shown to narrow the range?
- Are toy values reproducible?
- Is the final singleton interval checked?
- Are historical query counts labelled historical?
- Is OAEP itself not falsely called broken?
- Is RFC 8017's uniform-error requirement included?
- Does the ROCA transition clearly move to key-generation structure?

Any "no" means another revision.
