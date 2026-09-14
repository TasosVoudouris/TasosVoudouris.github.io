---
title: "Additive Secret Sharing: Linear Sharing over Finite Fields"
description: "Build the simplest linear secret-sharing scheme, prove reconstruction and privacy, and see why local addition/subtraction works directly on shares."
pubDate: "2025-05-17"
updatedDate: "2026-09-12"
topics:
- "Secret Sharing"
- "MPC"
- "Mathematical Foundations"
- "Cryptographic Engineering"
tags:
- "additive-secret-sharing"
- "linear-secret-sharing"
- "finite-fields"
- "mpc"
- "information-theoretic-security"
difficulty: "Introductory"
series: "Secret Sharing & Polynomial Tools"
seriesOrder: 1
sourcePath: "experiments/threshold-cryptography/additive"
draft: false
---
Additive secret sharing is the simplest useful example of a **linear secret-sharing scheme**. A value is represented as a collection of field elements whose sum equals the secret. The construction is elementary, but the linearity it exposes is exactly the property that later reappears in MPC protocols, threshold systems, and more structured polynomial-sharing schemes.

Throughout this article we work over the prime field $\mathbb{F}_q$. The code uses deliberately small toy parameters so that every intermediate value can be inspected; production systems require protocol-specific field sizes, authenticated communication, and cryptographically secure randomness.

*Additive Secret Sharing* is a foundational technique in Secure Multi-Party Computation (MPC). It enables a secret $s$ to be split into multiple *shares* such that each individual share reveals no information about $s$, but the secret can be reconstructed when all shares are combined.

This scheme operates over a finite field $\mathbb{Z}_q$, where $q$ is a small prime number. The code included in the folder the companion implementation showcases additive secret sharing over $\mathbb{Z}_{41}$ with $N = 5$ shares.


## Mathematical Background

Given a secret $s \in \mathbb{Z}_q$, the goal is to generate $N$ shares $s_1, s_2, \dots, s_N \in \mathbb{Z}_q$ such that:

$$
s \equiv \sum_{i=1}^N s_i \pmod{q}
$$


### Share Generation

* Randomly choose $N - 1$ shares: $s_1, \dots, s_{N-1} \in_R \mathbb{Z}_q$
* Define the final share $s_N$ as:

$$
s_N = \left(s - \sum_{i=1}^{N-1} s_i\right) \bmod q
$$

This ensures that the sum of all shares modulo $q$ equals the original secret $s$.

### Secret Reconstruction

Given all $N$ shares:

$$
s = \left(\sum_{i=1}^N s_i\right) \bmod q
$$

This reconstruction is exact and requires **all** shares (non-threshold).

Below we explain briefly the steps:

## Parameters

```python
Q = 41  # Prime field modulus
N = 5   # Number of shares
```

## Class Definition

```python
class Additive:
    def __init__(self, secret=None):
        self.secret = secret
        self.shares = self.additive_share(secret) if secret is not None else []
```

  * Initializes an instance with a given secret.
  * Automatically generates shares upon initialization if the secret is provided.

## Share Generation

```python
def additive_share(self, secret):
    shares = [secrets.randbelow(Q) for _ in range(N - 1)]
    shares.append((secret - sum(shares)) % Q)
    return shares
```

* Picks $N-1$ random shares.
* Ensures the final share makes the sum consistent with the secret modulo $Q$.

## Secret Reconstruction

```python
def additive_reconstruct(self):
    return sum(self.shares) % Q
```

## Linear Operations on Shared Values

```python
def __add__(x, y):
    z = Additive()
    z.shares = [(xi + yi) % Q for xi, yi in zip(x.shares, y.shares)]
    return z

def __sub__(x, y):
    z = Additive()
    z.shares = [(xi - yi) % Q for xi, yi in zip(x.shares, y.shares)]
    return z
```

These preserve correctness under modular arithmetic:

$$
[z]_i = ([x]_i \pm [y]_i) \bmod q, \qquad i=1,\ldots,N,
$$

so the reconstructed value is $z=(x\pm y)\bmod q$.

## Worked Example

```python
# Generate a secret and its shares
secret = secrets.randbelow(Q)
shares = [secrets.randbelow(Q) for _ in range(N - 1)]
shares.append((secret - sum(shares)) % Q)
```

Reconstruction:

```python
print(sum(shares) % Q)  # Should equal the original secret

x_secret = secrets.randbelow(Q)
x = Additive(x_secret)
print(x.reveal())  # Outputs the reconstructed secret

y_secret = secrets.randbelow(Q)
y = Additive(y_secret)
print(y.reveal())

z = x - y
print(z.reveal())  # Should match (x_secret - y_secret) % Q

assert z.reveal() == (x_secret - y_secret) % Q
```


* With uniformly random shares, the basic $N$-out-of-$N$ construction is **perfectly private** against every coalition that is missing at least one share.
* It is an $N$-out-of-$N$ scheme: all $N$ shares are required for reconstruction. The next article generalizes this idea to a true $t$-out-of-$n$ threshold using Shamir secret sharing.
* It supports efficient and correct addition/subtraction of secrets in the shared domain.

---

For a deeper understanding of Additive Secret Sharing and related topics in secure multiparty computation, consider exploring the following resources:

* **Books and Surveys**

  * Ronald Cramer, Ivan Damgård, and Jesper Buus Nielsen, *Secure Multiparty Computation and Secret Sharing*
  * Jonathan Katz and Yehuda Lindell, *Introduction to Modern Cryptography*
  * Oded Goldreich, *Foundations of Cryptography: Volume 2, Basic Applications*

* **Foundational Papers**

  * Andrew C. Yao, “Protocols for Secure Computations,” *FOCS*, 1982.
  * David Chaum, Claude Crépeau, and Ivan Damgård, “Multiparty Unconditionally Secure Protocols,” *STOC*, 1988.
