---
title: "Sponge Construction, Keccak, and SHA-3"
description: "Study absorb/squeeze sponge construction, Keccak-f[1600], SHA-3/SHAKE domain separation, and why sponge-based hashing differs structurally from Merkle–Damgård."
pubDate: "2026-08-12"
updatedDate: "2026-09-12"
topics:
  - "Hash Functions"
  - "Cryptographic Engineering"
tags:
  - "sha3"
  - "keccak"
  - "sponge"
  - "shake"
  - "fips-202"
difficulty: "Advanced"
series: "Hash Functions & MACs"
seriesOrder: 6
sourcePath: "experiments/hash-functions"
status: "Validated"
draft: false
---
## 1. A different architecture

SHA-3 is not “SHA-2 with more rounds.” SHA-2 iterates a compression function over a chaining state. SHA-3 uses a *sponge*: a fixed-width internal state is repeatedly transformed by a public permutation while message data is absorbed and output is squeezed.

For Keccak-f[1600], the state width is

\[
b=r+c=1600,
\]

where:

- (r), the **rate**, is the portion that directly interacts with input/output;
- (c), the **capacity**, is not directly exposed and supplies the generic security margin.

A larger rate means fewer permutation calls and better throughput. A larger capacity means a smaller rate at fixed width but stronger generic bounds. The rate/capacity split is part of each standardized function.

![Sponge absorption and squeezing](/images/hash-functions/sponge-keccak-sha3/sponge.png)

## 2. Absorb and squeeze

Given a padded message split into (r)-bit blocks (M_1,\ldots,M_q):

1. Initialize the entire (b)-bit state to zero.
2. For each block, XOR (M_i) into the rate portion and apply permutation (f):

   \[
   S\leftarrow f\big(S\oplus(M_i\|0^c)\big).
   \]

3. Read up to (r) output bits from the rate portion.
4. If more output is required, apply (f) again and read another rate-sized part.

Because squeezing can continue, the same framework supports fixed-output hashes and extendable-output functions (XOFs). The output length is an input to how a XOF is used; “the SHAKE256 digest” is incomplete without a requested length.

## 3. Standard FIPS 202 instances

| Function | Rate (r) | Capacity (c) | Output | Nominal classical strength stated by function name/use |
|---|---:|---:|---:|---|
| SHA3-224 | 1152 | 448 | 224 bits | 112-bit collisions, 224-bit preimages |
| SHA3-256 | 1088 | 512 | 256 bits | 128-bit collisions, 256-bit preimages |
| SHA3-384 | 832 | 768 | 384 bits | 192-bit collisions, 384-bit preimages |
| SHA3-512 | 576 | 1024 | 512 bits | 256-bit collisions, 512-bit preimages |
| SHAKE128 | 1344 | 256 | Variable | Up to 128-bit generic security with adequate output |
| SHAKE256 | 1088 | 512 | Variable | Up to 256-bit generic security with adequate output |

For a (d)-bit fixed digest, collision resistance cannot exceed (d/2), regardless of capacity. Asking SHAKE for too few output bits similarly caps the achieved preimage and collision strengths. Capacity-based sponge bounds also depend on total adversarial queries; consult the standard and construction proof for a formal bound.

## 4. Padding and domain separation

Keccak uses multi-rate padding `pad10*1`: append a `1`, zero or more `0` bits, and a final `1` so the result is a multiple of the rate. Standardized byte-oriented implementations combine this padding with a **delimited suffix** identifying the function domain.

| Function family | Byte-level delimited suffix in common implementations |
|---|---:|
| SHA3 fixed-output functions | `0x06` |
| SHAKE functions | `0x1f` |

The final block also has its most significant bit XORed with `0x80`. If a suffix occupies the last available rate byte, those operations combine in that byte.

This is why raw Keccak-256 and standardized SHA3-256 produce different results for the same message even though both use Keccak-f[1600] with a 1088-bit rate. The domain suffix is not cosmetic.

## 5. The Keccak-f[1600] state

The 1600 bits are arranged as (A[x,y,z]) with:

\[
x,y\in\{0,1,2,3,4\},\qquad z\in\{0,\ldots,63\}.
\]

For fixed (x,y), the 64 bits over (z) form a **lane**. Five lanes form a row or column depending on the coordinate held fixed; slices, sheets, and planes are alternative views useful in the design analysis.

![Keccak state terminology](/images/hash-functions/sponge-keccak-sha3/state.png)

Byte serialization is little-endian within each 64-bit lane. This differs from SHA-256's big-endian 32-bit word parsing and is a frequent source of implementations that look structurally correct but fail every standard vector.

## 6. The permutation round

Keccak-f[1600] applies 24 rounds. Each round is

\[
\iota\circ\chi\circ\pi\circ\rho\circ\theta.
\]

The order matters.

### 6.1 Theta: column-parity diffusion

Compute each column parity:

\[
C[x,z]=\bigoplus_{y=0}^{4}A[x,y,z].
\]

Then

\[
D[x,z]=C[x-1,z]\oplus C[x+1,z-1]
\]

with coordinates modulo 5 and lane-bit positions modulo 64. XOR (D[x,z]) into every lane bit in column (x). In 64-bit lane notation, the second term is a one-bit left rotation of (C[x+1]).

![Theta diffusion](/images/hash-functions/sponge-keccak-sha3/keccak-theta.png)

Theta is linear over (\mathrm{GF}(2)). It makes a difference in one column affect neighboring columns.

### 6.2 Rho: lane rotations

Rotate each lane left by a fixed offset (r[x,y]):

\[
B[x,y]=\operatorname{ROTL}_{64}(A[x,y],r[x,y]).
\]

The offsets are distinct by coordinate and derived from a traversal of the state. Lane ((0,0)) has offset zero.

![Rho lane rotation](/images/hash-functions/sponge-keccak-sha3/rho.png)

### 6.3 Pi: lane transposition

Move rotated lanes to new coordinates. One equivalent convention is

\[
B[y,\,2x+3y]=\operatorname{ROTL}_{64}(A[x,y],r[x,y]),
\]

with coordinates modulo 5. Rho and Pi are often implemented together to avoid a second temporary state.

![Pi lane movement](/images/hash-functions/sponge-keccak-sha3/pi.png)

### 6.4 Chi: nonlinear row mixing

For each row:

\[
A'[x,y]=B[x,y]\oplus\big((\neg B[x+1,y])\land B[x+2,y]\big).
\]

![Chi nonlinear propagation](/images/hash-functions/sponge-keccak-sha3/keccak-chi.png)

Chi is the round's only nonlinear step. Every output lane in a row must be computed from the unchanged input row; updating lanes in place and immediately reusing them changes the permutation. The implementation therefore copies each five-lane row first.

### 6.5 Iota: round constants

Finally:

\[
A'[0,0]\leftarrow A'[0,0]\oplus RC_i.
\]

The round constant breaks symmetries that would otherwise survive the identical round structure. It affects one lane directly; the following rounds diffuse its effect.

## 7. Why direct SHA-2 length extension does not transfer

A SHA-256 digest publishes its complete 256-bit chaining state. SHA3-256 outputs 256 bits from a 1088-bit rate portion of a 1600-bit state and leaves a 512-bit capacity hidden. The attacker cannot reconstruct the full post-squeeze state and simply resume it as in the SHA-256 secret-prefix lab.

This is a statement about that attack mechanism, not an endorsement of an improvised keyed sponge. For message authentication with the SHA-3 family, use KMAC as specified by [NIST SP 800-185](https://csrc.nist.gov/pubs/sp/800/185/final), or the exact construction mandated by the protocol.

## 8. SHA-3, SHAKE, cSHAKE, and KMAC

- **SHA3-(d):** fixed (d)-bit digest with the SHA-3 suffix.
- **SHAKE128/SHAKE256:** XOFs; the caller selects output length.
- **cSHAKE:** customizable SHAKE with standardized function-name and customization strings. When both are empty, it is aligned with SHAKE behavior as specified by SP 800-185.
- **KMAC:** a keyed message authentication code/PRF built from cSHAKE encodings. Its key, message, customization string, and output length have defined encodings and domains.
- **TupleHash:** hashes a tuple without ambiguous raw concatenation.
- **ParallelHash:** supports tree-style parallel processing of long strings.

These derived functions exist because “prepend a label/key somehow” is not a sufficient protocol specification.

## 9. Corrected implementation

[`code/sha3_educational.py`](https://github.com/TasosVoudouris/TasosVoudouris.github.io/blob/main/experiments/hash-functions/code/sha3_educational.py) implements:

- 25 little-endian 64-bit lanes;
- all 24 Keccak-f[1600] round constants;
- Theta, combined Rho/Pi, Chi, and Iota;
- byte-level multi-rate padding with `0x06` or `0x1f`;
- SHA3-256 with (r=1088,c=512);
- SHAKE256 with arbitrary output length;
- repeated squeezing when output exceeds one rate block.

The former code used a 512-bit rate for SHA3-256, converted the message through a big-endian integer, and selected ambiguous halves of the squeezed integer. Those choices define neither SHA3-256 nor a compatible Keccak instance.

The replacement is tested against `hashlib` for empty input, `abc`, messages of 135/136/137 bytes around the 136-byte rate boundary, and a 200-byte SHAKE256 output.

Run:

```bash
python code/sha3_educational.py
```

## 10. Implementation checklist

- Confirm the exact function: Keccak, SHA3, SHAKE, cSHAKE, or KMAC.
- Use the standardized rate, capacity, suffix, and output length.
- Treat lanes as little-endian and confirm coordinate flattening.
- Mask complement results to 64 bits in languages with unbounded integers.
- Compute Chi from an unchanged row.
- Test empty input, exact rate boundaries, multi-block messages, and multi-block XOF output.
- Use a maintained implementation for production and test against official vectors.

Primary specification: [NIST FIPS 202](https://csrc.nist.gov/pubs/fips/202/final). Derived functions: [NIST SP 800-185](https://csrc.nist.gov/pubs/sp/800/185/final).

Previous: [Length-Extension Attacks](/blog/length-extension-attacks/).

Next: [Message Authentication Codes](/blog/message-authentication-codes/).
