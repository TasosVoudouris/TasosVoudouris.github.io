# Additive Secret Sharing: A Formal Cryptographic Overview


*Additive Secret Sharing* is a foundational technique in Secure Multi-Party Computation (MPC). It enables a secret $s$ to be split into multiple *shares* such that each individual share reveals no information about $s$, but the secret can be reconstructed when all shares are combined.

This scheme operates over a finite field $\mathbb{Z}_q$, where $q$ is a small prime number. The code included in the folder `src/additive.py` showcases additive secret sharing over $\mathbb{Z}_{41}$ with $N = 5$ shares.


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

1. Parameters: 

```python
Q = 41  # Prime field modulus
N = 5   # Number of shares
```

2. Class Definition

```python
class Additive:
    def __init__(self, secret=None):
        self.secret = secret
        self.shares = self.additive_share(secret) if secret is not None else []
```

  * Initializes an instance with a given secret.
  * Automatically generates shares upon initialization if the secret is provided.

3. Share Generation

```python
def additive_share(self, secret):
    shares = [random.randrange(Q) for _ in range(N - 1)]
    shares.append((secret - sum(shares)) % Q)
    return shares
```

* Picks $N-1$ random shares.
* Ensures the final share makes the sum consistent with the secret modulo $Q$.

4. Secret Reconstruction

```python
def additive_reconstruct(self):
    return sum(self.shares) % Q
```

5. Addition and subtraction of two shared secrets:

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
(x \pm y) \mod q = (x_1 \pm y_1, \dots, x_N \pm y_N)
$$

And a simple example: 

```python
# Generate a secret and its shares
secret = random.randint(0, Q-1)
shares = [random.randrange(Q) for _ in range(N - 1)]
shares.append((secret - sum(shares)) % Q)
```

Reconstruction:

```python
print(sum(shares) % Q)  # Should equal the original secret

x_secret = random.randint(0, Q-1)
x = Additive(x_secret)
print(x.reveal())  # Outputs the reconstructed secret

y_secret = random.randint(0, Q-1)
y = Additive(y_secret)
print(y.reveal())

z = x - y
print(z.reveal())  # Should match (x_secret - y_secret) % Q

assert z.reveal() == (x_secret - y_secret) % Q
```


* This scheme is simple, linear, and **perfectly secure** against any subset of parties with fewer than $N$ shares.
* It is *non-threshold*: all $N$ shares are needed for reconstruction, we will talk about threshold cryptography in the future.
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



