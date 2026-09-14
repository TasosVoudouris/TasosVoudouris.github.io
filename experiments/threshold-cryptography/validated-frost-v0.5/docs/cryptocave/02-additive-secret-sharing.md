# Additive Secret Sharing

Additive sharing is the shortest route from a private number to distributed
state. To share $s\in\mathbb F_p$ among $n$ parties, sample $n-1$ uniform field
elements and choose the last share so that

$$
s_1+s_2+\cdots+s_n=s\pmod p.
$$

In code:

```python
shares = [rng.randrange(modulus) for _ in range(num_parties - 1)]
shares.append((secret - sum(shares)) % modulus)
```

Reconstruction is simply

$$
s=\sum_{i=1}^{n}s_i\pmod p.
$$

## Why a missing share hides the secret

Suppose an observer sees $n-1$ shares and guesses that the secret is $s'$. The
missing share

$$
s_n'=s'-\sum_{i=1}^{n-1}s_i\pmod p
$$

makes that guess perfectly consistent. The same argument works for every
$s'\in\mathbb F_p$. Consequently, every strict subset of an N-out-of-N additive
sharing has no information about the secret.

The function `explain_missing_share` preserves exactly this useful demonstration
from the original `sss.py`.

## Linear operations

If $[x]=(x_1,\ldots,x_n)$ and $[y]=(y_1,\ldots,y_n)$, parties can compute

$$
[x]+[y]=(x_1+y_1,\ldots,x_n+y_n)
$$

without opening either secret. Subtraction and multiplication by a public
scalar work similarly. These are local operations: no party needs another
party's share.

Multiplying two private additive sharings is different. Products $x_i y_i$ do
not sum to $xy$ because the cross terms are missing. Secure multiplication
requires interaction or correlated preprocessing, such as a Beaver triple.

## What additive sharing does not provide

The scheme is simple but rigid: all $n$ shares are required. One unavailable
party prevents reconstruction. It also provides privacy only; a malicious party
can send an arbitrary value during reconstruction.

Shamir sharing introduces a configurable threshold and redundancy while
preserving the useful local linear operations.

Next: [Shamir secret sharing](03-shamir-secret-sharing.md).
