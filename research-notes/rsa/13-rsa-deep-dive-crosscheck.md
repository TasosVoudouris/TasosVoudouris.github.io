# RSA Deep Dive I — Cross-Check Audit

## Goal

Begin the new topic-closing workflow:

```text
foundation posts
-> intermediate deep dives
-> attacks
-> mitigations / standards
-> topic synthesis
```

RSA is the first block.

This post focuses only on the insecurity of raw textbook RSA encryption.

---

## Sources compared

### Current Cryptography From Zero

Checked:

- `src/cryptozero/attacks/rsa_toy.py`
- `chapters/08_rsa_attacks/README.md`
- `chapters/08_rsa_attacks/demo.py`

Current material already contains:

```text
textbook_rsa_is_deterministic(...)
```

and explicitly states that raw RSA requires a secure randomized
encoding/padding construction.

The current attack module did not yet include the multiplicative CCA demo, so
the Deep Dive companion script adds that pedagogical experiment.

---

## Old CryptoCave RSA material

Checked:

```text
Asymmetric/RSA/RSA.md
```

The old notes correctly derive:

```text
E(M1*M2) = E(M1)*E(M2) mod N.
```

They also correctly warn not to use raw textbook RSA.

However, the old section described RSA as providing "multiplicative homomorphic
encryption" and then mixed useful-homomorphism language with security warnings.

The newer revision notes had already identified the better framing:

```text
textbook RSA multiplicativity
-> primarily malleability/security failure
```

That mature interpretation is used in the public article.

---

## Mature CryptoBible material

The newer RSA chapter explicitly states that textbook RSA is:

```text
deterministic
multiplicatively malleable
unsuitable as a modern encryption scheme
```

and separates the RSA primitive from complete schemes such as RSAES-OAEP.

This is the central conceptual framing of Deep Dive I.

---

## Toy example

Use the Blog 12 key:

```text
N = 3233
e = 17
d = 413
```

Target:

```text
m = 42
```

Textbook ciphertext:

```text
c = 42^17 mod 3233 = 2557
```

### Determinism

Repeated encryption gives:

```text
2557
2557
```

### Malleability

Choose:

```text
r = 2
```

Then:

```text
r^e mod N = 1752
c' = c * r^e mod N = 2159
```

Decrypt:

```text
(c')^d mod N = 84 = 42*2
```

### Textbook chosen-ciphertext recovery

Because:

```text
2^(-1) mod 3233 = 1617
```

the attacker recovers:

```text
84 * 1617 mod 3233 = 42
```

All values were computationally checked.

---

## Security interpretation

The attack does not:
- factor N;
- recover d;
- exploit a timing channel;
- exploit a fault;
- weaken modular exponentiation.

It exploits algebraic malleability of the raw encryption map.

This is a scheme-level failure.

---

## OAEP framing

The post deliberately avoids calling OAEP "just padding".

The important architecture is:

```text
message
-> randomized structured encoding
-> integer representative
-> RSAEP
-> ciphertext
```

RFC 8017 specifies:
- RSAES-OAEP;
- RSAES-PKCS1-v1_5.

It states that RSAES-OAEP is required to be supported for new applications,
while RSAES-PKCS1-v1_5 is retained for compatibility.

---

## OAEP nuance retained from mature notes

The post does NOT say:

```text
OAEP solves every RSA security problem.
```

The mature notes correctly preserve the security-proof nuance and mention that
decoding behavior can still create oracles.

Bleichenbacher and Manger are therefore previewed but deferred to dedicated
RSA Deep Dives.

---

## Bulk encryption correction

The mature material explicitly rejects an old "split a file into RSA-sized
blocks" habit.

The public article preserves the modern systems pattern:

```text
public-key mechanism
-> compact keying material
-> KDF / key schedule
-> AEAD
```

OAEP's payload bound is mentioned only to reinforce this architecture.

---

## Companion code

Added:

```text
repo/chapters/13_rsa_textbook_failures/demo.py
```

This is standalone educational code and uses the same tiny RSA key as Blog 12.

It demonstrates:
- determinism;
- malleability;
- textbook chosen-ciphertext recovery.

No real target interaction or deployment attack code is included.

---

## Next RSA block

Recommended order:

```text
Deep Dive I   textbook RSA failures        [this post]
Deep Dive II  common-modulus attack
Deep Dive III Håstad broadcast attack
Deep Dive IV  Wiener small-d attack
Deep Dive V   Bleichenbacher oracle
Deep Dive VI  Coppersmith / small roots
Deep Dive VII RSA attack map / synthesis
```

Blog 09 already covers CRT fault attacks and will be linked into the final RSA
attack map rather than duplicated.

---

## Publication review

Before publication, verify:

- Is primitive vs scheme clear?
- Does determinism obviously break privacy?
- Is multiplicativity framed as malleability rather than a secure HE feature?
- Can the reader follow `2557 -> 2159 -> 84 -> 42`?
- Is the CCA oracle assumption explicit?
- Does OAEP look like cryptographic encoding rather than cosmetic padding?
- Is OAEP not oversold?
- Is RSA clearly positioned as non-bulk encryption?
- Do prerequisite links reduce repetition?
- Does the next Common-Modulus post feel like a genuine deeper step?

Any "no" means another edit pass.
