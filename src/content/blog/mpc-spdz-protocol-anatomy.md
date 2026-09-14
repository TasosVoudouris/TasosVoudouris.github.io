---
title: "SPDZ Protocol Anatomy: Preprocessing, Inputs, Multiplication, Openings, and MAC Checks"
description: "Assemble authenticated shares and Beaver triples into the SPDZ online workflow, explain what is preprocessed, what is opened, and what must be checked before a result is accepted."
pubDate: "2025-03-11"
updatedDate: "2026-09-14"
topics:
  - "MPC"
  - "Secret Sharing"
  - "Cryptographic Engineering"
tags:
  - "spdz"
  - "preprocessing"
  - "beaver-triples"
  - "mac-check"
  - "arithmetic-circuits"
  - "active-security"
difficulty: "Advanced"
status: "Reviewed"
series: "Secure Multiparty Computation"
seriesOrder: 4
draft: false
---
Now we can place the pieces in their actual protocol roles.

The recovered material mixed three generations of ideas:

1. simple replicated/additive secret sharing;
2. Beaver-triple arithmetic in a passive trusted-preprocessing model;
3. notes labelled SPDZ that discussed active security but whose code did not implement it.

This chapter gives the clean map.

## 1. Preprocessing model

SPDZ separates the expensive cryptographic work from the latency-sensitive private-input computation.

### Offline/preprocessing

Generate correlated authenticated randomness, especially multiplication triples

$$
[a], [b], [c],\qquad c=ab.
$$

The brackets now mean **authenticated secret shares**.

### Online

Once inputs are known, evaluate the arithmetic circuit using local linear operations and cheap masked openings for multiplication.

## 2. Input sharing

A private input $x$ must enter the authenticated-sharing world.

Conceptually the parties need shares $x_i$ and MAC shares $\gamma_i$ satisfying

$$
\sum_i x_i=x,
$$

$$
\sum_i\gamma_i=\alpha x.
$$

The exact input protocol depends on who owns the input and which SPDZ-family variant is used.

The key point is that a raw additive share is not enough for malicious security.

## 3. Addition gate

For authenticated values $[x]$ and $[y]$:

$$
[z]=[x]+[y]
$$

is local on both components:

$$
z_i=x_i+y_i,
$$

$$
\gamma_{z,i}=\gamma_{x,i}+\gamma_{y,i}.
$$

No communication round is needed.

## 4. Multiplication gate

Consume an authenticated triple

$$
[a],[b],[c],\quad c=ab.
$$

Compute

$$
[e]=[x]-[a],
$$

$$
[f]=[y]-[b].
$$

Open $e$ and $f$ using the protocol's authenticated opening procedure.

Then

$$
[xy]=[c]+e[b]+f[a]+ef.
$$

All terms now preserve the authentication relation.

## 5. Why preprocessing quality is security-critical

Suppose an attacker supplies

$$
c\ne ab.
$$

Then even honest online computation produces a wrong multiplication result.

Therefore active security must validate preprocessing correlations. SPDZ-family systems use checks such as **sacrifice** and, in later variants, alternative triple-generation techniques.

The old toy's

```python
generate_mul_triple()
```

inside the process assumes an honest trusted dealer. That is acceptable for demonstrating the Beaver identity but not a replacement for secure preprocessing.

## 6. Opening is a protocol, not a helper function

Toy code often contains:

```python
reconstruct(shares)
```

as a local Python call.

In a distributed adversarial setting, opening means:

1. parties transmit opening shares;
2. messages are associated with a session/value identifier;
3. malformed or missing messages are handled;
4. the public value is reconstructed;
5. authentication is checked;
6. the protocol either accepts or aborts.

That distinction is the same lesson we encountered in VSS, DKG, and FROST: a mathematically valid equation is only one layer of a distributed protocol.

## 7. Batch MAC checks

Checking every opened value separately can be expensive. SPDZ-style protocols can aggregate authentication checks with random linear combinations.

The intuition is familiar from polynomial/proof-system batching: a malicious error vector is unlikely to cancel under a fresh random challenge unless all relations are valid.

This reduces verification overhead while preserving detection probability.

## 8. Dishonest majority

A major attraction of the SPDZ line is active security even when a majority of participants may be corrupt, under the scheme's computational assumptions and preprocessing construction.

That is very different from an information-theoretic Shamir protocol that assumes an honest threshold.

It also explains why SPDZ preprocessing is substantially more sophisticated than drawing a random triple in one Python process.

## 9. Online performance

After preprocessing, the online cost has a useful shape:

- additions: local;
- public-scalar multiplication: local;
- multiplication: one masked opening layer plus local arithmetic;
- many independent gates: batchable in one round.

Therefore arithmetic-circuit depth and network latency matter as much as CPU instruction count.

## 10. From original SPDZ to later preprocessing

The recovered notes mention the historical progression from homomorphic-encryption-based preprocessing to later OT-based approaches such as MASCOT.

That progression changes **how the authenticated triples are generated**, while preserving the high-level online arithmetic interface.

This separation is one of the strongest software-engineering ideas in the protocol family: the online evaluator can consume preprocessed correlations without caring about every cryptographic detail used to create them.

## 11. Takeaway

The clean protocol stack is:

```text
secure preprocessing
      ↓
authenticated shares/triples
      ↓
local linear arithmetic
      ↓
masked openings for multiplication
      ↓
batched MAC verification
      ↓
accept / abort
```

That is the conceptual SPDZ pipeline. The next chapter focuses on the parts toy implementations most often omit.
