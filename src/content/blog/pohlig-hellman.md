---
title: "Discrete Logarithms III: Pohlig–Hellman"
description: "A focused treatment of the Pohlig–Hellman algorithm and why smooth group order changes the effective difficulty of the discrete logarithm problem."
pubDate: "2025-05-26"
updatedDate: '2026-09-12'
topics:
- "Discrete Logarithms"
- "Cryptanalysis"
- "Number Theory"
tags:
- "pohlig-hellman"
- "smooth-order"
- "dlp"
- "crt"
difficulty: "Advanced"
series: "Discrete Logarithm Algorithms"
seriesOrder: 3
sourcePath: "experiments/ready-material/discrete-log"
draft: false
---
The **Pohlig–Hellman algorithm** is a powerful method for solving the DLP in a finite abelian group $G$, particularly when the group order is *smooth*, i.e., its prime factorization consists of small primes. The algorithm reduces the DLP in a large group to DLPs in smaller subgroups of prime power order. 🎥 Nice Explanation: [Jim Fowler – Pohlig–Hellman DLP](https://www.youtube.com/watch?v=B0p0jbCGvWk&ab_channel=JimFowler)

Let $G$ be a finite abelian group of order $n$. The DLP in $G$ is at most as difficult as the DLP in its *largest prime-order subgroup*.

* Even if $G$ is not cyclic, each element $g \in G$ generates a subgroup $\langle g \rangle \subseteq G$ of order $\operatorname{ord}(g)$.
* In practice, the Pohlig–Hellman algorithm is efficient when the group order $n$ is *B-smooth* (i.e., all prime factors of $n$ are less than or equal to a small bound $B$).

A high level overview of the core components is illustrated below: 


<p align="center">
  <img src="/images/ready/pohlig-hellman/pohlig.PNG" alt="Pohlig–Hellman Illustration">
</p>



### Smooth Numbers

A number $N$ is called **B-smooth** if all of its prime divisors are $\leq B$.

If the order of the group is smooth (e.g., $n = p_1^{e_1} \cdots p_r^{e_r}$), we can solve the DLP by:

1. Solving it in each subgroup of order $p_i^{e_i}$,
2. Combining the results using the *Chinese Remainder Theorem (CRT)*.

Now, we briefly explain the steps of the algorithm. A full Python implementantion can be found in `src/pohlighellman.py`. 


First we have to define our group, so let:

* $G$ be a group with order $n = q^e$,
* $g \in G$, $h = g^x \in G$,
* Goal: recover $x \in \mathbb{Z}_{q^e}$.

We compute $x$ in base-$q$ expansion:

$$
x = x_0 + x_1 q + x_2 q^2 + \cdots + x_{e-1} q^{e-1}
$$

We provide a pseudocode of the DLP in $G$ with $|G| = q^e$ for those who want to implement it:

```text
Input: Generator g ∈ G of order q^e, target h ∈ G
Output: x such that g^x = h

1. Set x ← 0
2. Compute g_q ← g^{q^{e−1}} mod p
3. For j = 0 to e − 1:
    a. Compute h_j ← (g^{-x} * h)^{q^{e−1−j}} mod p
    b. Solve discrete log: g_q^{x_j} = h_j mod p
    c. Update x ← x + x_j * q^j
```

We proceed by defining the DLP in a general group of smooth order. So, let: 

* $|G| = n = \prod_{i=1}^r q_i^{e_i}$ be the prime factorization of the group order,
* $g \in G$ a generator, $h = g^x \in G$,
* Goal: recover $x \in \mathbb{Z}_n$.

The idea is the following: 

* Solve $g^x = h$ modulo each $q_i^{e_i}$,
* Use the *Chinese Remainder Theorem (CRT)* to reconstruct $x \mod n$.

A pseudocode of the Pohlig–Hellman Algorithm in the General Case: 

```text
Input: Generator g ∈ G of order n, target h ∈ G
Output: x such that g^x = h

1. Factor n = ∏ q_i^{e_i}
2. For each i from 1 to r:
    a. Let n_i ← q_i^{e_i}
    b. Compute g_i ← g^{n / n_i} mod p
    c. Compute h_i ← h^{n / n_i} mod p
    d. Use previous subroutine to solve DLP in ⟨g_i⟩: find x_i ≡ x mod n_i
3. Use Chinese Remainder Theorem to combine all x_i mod n_i → get x mod n
```

To summarize, we need to note that the *Pohlig–Hellman algorithm* is especially effective when:

* The group order is **B-smooth**, i.e., its prime factors are small,
* The DLP can be efficiently solved in each smaller subgroup.

It is a *powerful optimization* over generic DLP solvers (like BSGS we saw at Part 2), especially for groups like $\mathbb{Z}_p^*$ where $p-1$ is smooth.
