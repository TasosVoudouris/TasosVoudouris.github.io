---
title: "Lattices & Lattice-Based Cryptography IX: Breaking Toy NTRU with LLL — From Public Key to a Short Secret Vector"
description: "A complete worked N=7 NTRU lattice attack: construct the public circulant matrix, prove that the secret lies in the lattice, run LLL, and recover an equivalent private key."
pubDate: "2022-06-21"
updatedDate: "2026-09-14"
topics:
- "Lattice Theory"
- "Lattice Methods"
- "Post-Quantum Cryptography"
- "Cryptanalysis"
- "Public-Key Cryptography"
tags:
- "ntru"
- "lll"
- "ntru-lattice"
- "circulant-matrix"
- "short-vector"
- "ross-course"
difficulty: "Advanced"
status: "Validated"
series: "Lattices & Lattice-Based Cryptography"
seriesOrder: 9
sourcePath: "experiments/lattices/ross-course"
draft: false
---
The previous NTRU article explains the scheme and its lattice geometry in general terms. This article does the full attack on a deliberately tiny instance.

The recovered course notebooks are particularly useful because they preserve the whole progression:

1. construct a valid NTRU key;
2. express multiplication by the public polynomial as a circulant matrix;
3. build the public $2N$-dimensional NTRU lattice;
4. prove that $(f,g)$ is a lattice vector;
5. run LLL;
6. recover a short pair that is equivalent to the original private key.

The original notebook asks several questions without fully explaining why the answers work. Here we fill in those gaps.

![Toy NTRU lattice construction and LLL recovery](/images/blog/lattices/ntru-lll-attack.svg)

## 1. Toy parameters

We use

$$
N=7,
\qquad
p=3,
\qquad
q=41.
$$

Work in

$$
R=\mathbb Z[x]/(x^7-1).
$$

The private polynomial is

$$
f=x^6-x^4+x^3+x^2-1.
$$

In coefficient-vector form, ordered from the constant coefficient upward,

$$
f=(-1,0,1,1,-1,0,1).
$$

The second small secret polynomial is

$$
g=x^6+x^4-x^2-x,
$$

so

$$
g=(0,-1,-1,0,1,0,1).
$$

The notebook verifies that $f$ is invertible modulo both $p$ and $q$ in the quotient ring.

## 2. Public key

Under the convention used in this notebook,

$$
h=f_q^{-1}g
\pmod{(q,x^7-1)}.
$$

The public key is

$$
h=
20x^6+40x^5+2x^4+38x^3+8x^2+26x+30.
$$

As a coefficient vector:

$$
h=(30,26,8,38,2,40,20).
$$

Because

$$
h=f_q^{-1}g,
$$

we have

$$
\boxed{fh\equiv g\pmod{(q,x^7-1)}}.
$$

That congruence is the entire reason the NTRU lattice contains the secret.

## 3. Lift the congruence back to the integers

Treat the coefficients of $h$ as integers rather than residues modulo $41$.

Then the recovered notebook computes

$$
fh-g
\equiv
41x^6+41x^4+41x^2+41x
\pmod{x^7-1}.
$$

Therefore

$$
fh-g=q u
\pmod{x^7-1},
$$

with

$$
u=x^6+x^4+x^2+x.
$$

Rearrange:

$$
fh-qu=g.
$$

This has exactly the form required by the public lattice construction.

## 4. Multiplication by h as a matrix

Cyclic polynomial multiplication in

$$
\mathbb Z[x]/(x^7-1)
$$

is a linear map on coefficient vectors.

For the public polynomial $h$, this map is represented by the circulant matrix

$$
H=
\begin{pmatrix}
30&26& 8&38& 2&40&20\\
20&30&26& 8&38& 2&40\\
40&20&30&26& 8&38& 2\\
 2&40&20&30&26& 8&38\\
38& 2&40&20&30&26& 8\\
 8&38& 2&40&20&30&26\\
26& 8&38& 2&40&20&30
\end{pmatrix}.
$$

The precise row/column convention matters when implementing the attack. What matters mathematically is consistency between the polynomial coefficient ordering and the linear map.

## 5. Build the public NTRU lattice

Use the row-basis convention

$$
M_h=
\begin{pmatrix}
I&H\\
0&qI
\end{pmatrix}.
$$

This is a $14\times14$ integer matrix.

A generic integer coefficient row vector

$$
(a,b)
$$

produces

$$
(a,b)M_h
=
(a,aH+qb).
$$

Now choose

$$
a=f,
\qquad
b=-u.
$$

Because

$$
fH-qu=g,
$$

we obtain

$$
\boxed{(f,-u)M_h=(f,g)}.
$$

Therefore

$$
\boxed{(f,g)\in\mathcal L(M_h)}.
$$

This is the rigorous version of the informal statement "the NTRU private key is a short vector in the public NTRU lattice."

## 6. Why the secret is geometrically unusual

The public lattice contains vectors with coordinates naturally involving $q=41$.

The secret vectors, however, use coefficients only from

$$
\{-1,0,1\}.
$$

The squared Euclidean norm of $(f,g)$ is only

$$
\|(f,g)\|^2=9.
$$

So the secret is extraordinarily short compared with generic lattice vectors in this tiny instance.

That is exactly the situation lattice reduction algorithms are designed to exploit.

## 7. Run LLL

Applying LLL to $M_h$ does not necessarily return the literal $(f,g)$ as the first row.

This is important.

A lattice can contain many short vectors, and NTRU has additional algebraic symmetries from multiplication by monomials and units in the quotient ring.

The reduced basis contains, among other short vectors, the pair

$$
\phi
=
-x^6-x^5+x^3-x^2+1,
$$

$$
\gamma
=
x^5+x^4-x^2-1.
$$

Their coefficient vectors are

$$
\phi=(1,0,-1,1,0,-1,-1),
$$

$$
\gamma=(-1,0,-1,0,1,1,0).
$$

This pair also has squared norm $9$.

## 8. Why an "equivalent" key is enough

The original worksheet then multiplies both polynomials by

$$
-x^4
$$

inside

$$
\mathbb Z[x]/(x^7-1).
$$

Because multiplication by $x^4$ is a cyclic coefficient rotation, we obtain

$$
-x^4\phi
\equiv
f
\pmod{x^7-1},
$$

and

$$
-x^4\gamma
\equiv
g
\pmod{x^7-1}.
$$

Our validated companion code reproduces exactly this equivalence:

```text
short LLL vector:
[1, 0, -1, 1, 0, -1, -1, -1, 0, -1, 0, 1, 1, 0]

after multiplication by -x^4 mod (x^7-1):
f = [-1, 0, 1, 1, -1, 0, 1]
g = [0, -1, -1, 0, 1, 0, 1]

PASS: LLL recovers an NTRU-equivalent short secret pair.
```

This teaches an important cryptanalytic lesson:

> an attacker does not necessarily need the exact original secret representation; an equivalent short key can be sufficient.

## 9. What LLL has actually accomplished

LLL guarantees a reduced basis, not an exact solution to SVP in arbitrary high dimension.

In this toy instance:

- the dimension is only $14$;
- $q$ is only $41$;
- secret coefficients are exceptionally small;
- the secret is therefore visible to basic reduction.

For real parameters, the security question is much more quantitative:

- lattice dimension;
- determinant and volume;
- expected shortest-vector length;
- secret and error distributions;
- root-Hermite factors;
- BKZ block size;
- sieving/enumeration costs;
- classical versus quantum attack models.

So the correct conclusion is **not** "LLL breaks NTRU."

The correct conclusion is:

> tiny NTRU instances make the secret-lattice geometry visible enough that LLL demonstrates exactly what a real lattice attack is trying to achieve.

## 10. A subtle convention issue

NTRU descriptions differ in where the factor $p$ is placed.

One common convention uses

$$
h=p g f_q^{-1}\pmod q
$$

and encryption

$$
e=rh+m.
$$

The recovered notebook instead uses

$$
h=g f_q^{-1}\pmod q
$$

and encryption

$$
e=prh+m.
$$

These are compatible conventions when used consistently.

A surprisingly common educational implementation bug is to take key generation from one convention and encryption from the other. That changes the decryption algebra and usually breaks correctness.

## 11. Relation to modern lattice cryptanalysis

The same workflow reappears throughout lattice cryptanalysis:

1. translate algebraic information into integer linear relations;
2. construct a lattice whose special vectors encode hidden information;
3. scale/weight coordinates so the target is geometrically short;
4. reduce the basis;
5. interpret one or more short vectors back in the original algebraic problem.

Coppersmith attacks, Hidden Number Problem attacks, partial-key exposure, and many structured lattice attacks differ in their lattice construction, but this basic pattern is remarkably persistent.

## 12. Companion implementation

The cleaned experiment is:

```text
experiments/lattices/ross-course/ntru_lll_attack.py
```

It is dependency-free and contains:

- the exact public circulant matrix from the recovered notebook;
- the $14\times14$ block NTRU lattice;
- an exact rational-arithmetic educational LLL implementation;
- detection of the equivalent short key;
- the $-x^4$ transformation recovering the original $f$ and $g$.

This makes the old Sage worksheet reproducible without depending on notebook state or an old CoCalc environment.

## Final lesson

The public key is not merely a polynomial.

It is also a compact description of a structured lattice.

The private key is not merely a pair of polynomials.

It is also an unusually short lattice vector.

NTRU security lives in the gap between those two descriptions: the legitimate user knows which short vector matters, while the attacker sees only the public lattice and must search its high-dimensional geometry.
