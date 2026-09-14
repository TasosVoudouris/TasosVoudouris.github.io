---
title: "Elliptic Curve Cryptanalysis III: Smart’s Attack on Anomalous Curves"
description: "A detailed introduction to the p-adic lifting machinery behind Smart’s attack on anomalous elliptic curves, including Hensel lifting and formal-group ideas."
pubDate: "2025-05-26"
updatedDate: '2026-09-12'
topics:
- "Elliptic Curve Theory"
- "Elliptic-Curve Cryptography"
- "Discrete Logarithms"
- "Cryptanalysis"
- "Number Theory"
tags:
- "smart-attack"
- "anomalous-curves"
- "p-adic"
- "hensel-lifting"
- "ecdlp"
difficulty: "Advanced"
series: "Elliptic Curve Cryptanalysis"
seriesOrder: 3
sourcePath: "experiments/ready-material/discrete-log"
draft: false
---
The *Smart attack*, introduced by Nigel Smart in 1999, targets a specific class of elliptic curves where the number of points on the curve over a finite field equals the size of the field. That is, the trace of Frobenius satisfies:

$$
t = 1 \quad \Rightarrow \quad \#E(\mathbb{F}_p) = p
$$

Let $P \in E(\mathbb{F}_p)$ be a point of prime order $n = p$, and suppose we are given a point $Q = kP$. The goal is to compute the discrete logarithm $k$.

The *key idea* of the attack is to lift the elliptic curve and its points from the finite field $\mathbb{F}_p$ to the $p$-adic field $\mathbb{Q}_p$, where more powerful number-theoretic tools are available, and then use this information to recover the discrete logarithm.

## $p$-adic Numbers: A Mathematical Primer

To carry out this attack, we must understand the basics of $p$-adic numbers, a rich and subtle number system that completes the rational numbers in a different way than the real numbers do.

### The $p$-adic Field $\mathbb{Q}_p$

Let $p$ be a prime number. Then:

* Every non-zero rational number $r \in \mathbb{Q}$ can be uniquely written in the form:

  $$
  r = p^n \cdot \frac{a}{b}
  $$

  where $a, b \in \mathbb{Z}$, $\gcd(a, p) = \gcd(b, p) = 1$, and $n \in \mathbb{Z}$.

* The $p$-adic absolute value is defined as:

  $$
  |r|_p = p^{-n}
  $$

  which induces a non-Archimedean metric.

* The *completion* of $\mathbb{Q}$ with respect to this absolute value yields the *$p$-adic field* $\mathbb{Q}_p$. This field contains infinite expansions of the form:

  $$
  x = x_0 + x_1p + x_2p^2 + x_3p^3 + \cdots
  $$

  where $x_i \in \{0, 1, \ldots, p-1\}$. If all $x_i = 0$ for $i < 0$, the resulting object lies in the ring of $p$-adic integers $\mathbb{Z}_p$.

These constructions allow algebraic and analytic tools to work in modular arithmetic settings, enabling advanced techniques like Hensel's lemma.

## Hensel’s Lemma and Lifting Roots

*Hensel’s Lemma* allows us to lift roots of polynomials modulo $p^e$ to roots modulo $p^{e+1}$, under certain conditions. It is the cornerstone of lifting from $\mathbb{F}_p$ to $\mathbb{Q}_p$.

Let $f(x) \in \mathbb{Z}[x]$, and suppose:

* $r$ is a root of $f \mod p^e$,
* $f'(r) \not\equiv 0 \mod p$, and
* $u$ is the inverse of $f'(r) \mod p$.

Then:

$$
r' = r - u \cdot f(r)
$$

satisfies:

$$
r' \equiv r \mod p^e \quad \text{and} \quad f(r') \equiv 0 \mod p^{e+1}
$$

This process can be iterated, much like Newton’s method, to obtain roots modulo $p^k$ for increasing $k$. In the Smart attack, this technique is used to lift points from $E(\mathbb{F}_p)$ to $E(\mathbb{Q}_p)$.

## Lifting Elliptic Curve Points

The Smart attack proceeds by:

1. *Lifting the elliptic curve* $E/\mathbb{F}_p$ to a corresponding curve $\widetilde{E}/\mathbb{Q}_p$.
2. *Lifting points* $P, Q \in E(\mathbb{F}_p)$ to $\widetilde{P}, \widetilde{Q} \in \widetilde{E}(\mathbb{Q}_p)$.
3. Using properties of the *formal group* associated to $\widetilde{E}$, exploiting the trace $t = 1$, to reduce the problem to a linear equation in $\mathbb{Q}_p$ where $k$ can be recovered using the $p$-adic logarithm or Newton-like methods.

This lifting framework breaks the problem out of the finite field and into a domain where the group structure behaves analytically, allowing *deterministic recovery* of the discrete log $k$ for weakly parameterized curves.

## Reduction and Formal Group Structure

In the *Smart attack*, we exploit the interplay between the elliptic curve group over the finite field $\mathbb{F}_p$ and its lift to the $p$-adic field $\mathbb{Q}_p$.

Let $E/\mathbb{Q}_p$ be the lift of an elliptic curve defined over $\mathbb{F}_p$. Then, there exists a *reduction modulo $p$* map:

$$
\pi: E(\mathbb{Q}_p) \to E(\mathbb{F}_p)
$$

which is a **group homomorphism**.

### The Kernel of Reduction

Let $E_1(\mathbb{Q}_p)$ denote the kernel of this reduction:

$$
E_1(\mathbb{Q}_p) = \{ R \in E(\mathbb{Q}_p) \mid \pi(R) = \mathcal{O} \}
$$

That is, $E_1(\mathbb{Q}_p)$ consists of all $p$-adic points that reduce to the point at infinity on the curve over $\mathbb{F}_p$.

By lifting the points $P$ and $Q = kP \in E(\mathbb{F}_p)$ to $\widetilde{P}, \widetilde{Q} \in E(\mathbb{Q}_p)$, we obtain a relation that lies entirely within this formal group structure.


### The $p$-adic Logarithm

We use a logarithmic map, denoted $\varphi_p$, from $E_1(\mathbb{Q}_p)$ into the additive group $p\mathbb{Z}_p$. For a point $S \in E_1(\mathbb{Q}_p)$, it is defined (to first order) by:

$$
\varphi_p(S) = -\frac{x(S)}{y(S)} \mod p^2
$$

This function behaves like a *logarithm* in the sense that:

$$
\varphi_p(aS + bT) \approx a\varphi_p(S) + b\varphi_p(T)
$$

modulo higher powers of $p$, and is particularly useful for linearizing the group operation in the formal group.


## Smart’s Attack Strategy

Let us outline the attack step by step. We are given:

* A curve $E/\mathbb{F}_p$ with trace $t = 1 \Rightarrow \#E(\mathbb{F}_p) = p$
* Points $P, Q = kP \in E(\mathbb{F}_p)$
* Our goal: recover the scalar $k$

Below we breifly discuss the steps: 

1. **Lift the Curve to $\mathbb{Q}_p$**:

   * Construct a lift $\widetilde{E}/\mathbb{Q}_p$ of $E/\mathbb{F}_p$, ensuring it reduces modulo $p$ to $E$.
   * A typical form:

     $$
     y^2 = x^3 + p\cdot a'x + b_0 + p\cdot b'
     $$

     where $a', b' \in \mathbb{Z}_p$ are chosen randomly to avoid pathological cases.

2. **Lift the Points $P, Q$ to $\mathbb{Q}_p$**:

   * Let $x(P') = x(P)$ and lift $y(P')$ via Hensel’s lemma to ensure that the equation holds over $\mathbb{Q}_p$.
   * Repeat for $Q \rightarrow Q'$.

3. **Use the Kernel Structure**:

   * Since $Q = kP$ in $E(\mathbb{F}_p)$, we know:

     $$
     Q' - kP' \in E_1(\mathbb{Q}_p)
     $$

     because it reduces to $\mathcal{O}$ in $\mathbb{F}_p$.

4. **Multiply Both Sides by $p$**:

   * The point $pP' \in E_1(\mathbb{Q}_p)$ and similarly $pQ' \in E_1(\mathbb{Q}_p)$, so:

     $$
     pQ' - k(pP') \in E_2(\mathbb{Q}_p)
     $$

     which is a deeper layer in the formal group filtration.

5. **Apply the $p$-adic Logarithm**:

   * Use the logarithm map $\varphi_p$ to obtain:

     $$
     \varphi_p(pQ') - k \cdot \varphi_p(pP') \in p\mathbb{Z}_p
     $$
   * Since all elements now lie in $p\mathbb{Z}_p$, reduce modulo $p$:

     $$
     k \equiv \frac{\varphi_p(pQ')}{\varphi_p(pP')} \mod p
     $$

6. **Recover $k$**:

   * Perform the division in $\mathbb{Z}/p\mathbb{Z}$. If the denominator is invertible, then:

     $$
     k = \left( \frac{\varphi_p(pQ')}{\varphi_p(pP')} \right) \mod p
     $$


So, to conclude, the Smart attack shows that elliptic curves with trace $t = 1$ (i.e., $\#E(\mathbb{F}_p) = p$) are insecure! Curves, like the ones explained, should be *avoided in cryptographic applications*. The Smart attack is a striking example of how deep mathematical tools—like p-adic analysis and Hensel’s lemma—can be used to break seemingly secure systems.

We provide a SageMath implementantion in `src/smartattackECDLP.sage`. For a Python implemenation and many more you can visit https://github.com/elliptic-shiho/ecpy.
