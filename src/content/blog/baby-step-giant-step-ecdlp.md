---
title: "Discrete Logarithms II: Baby-Step Giant-Step for ECDLP"
description: "A step-by-step implementation-oriented explanation of Shanks’s baby-step giant-step method for solving small elliptic-curve discrete logarithms."
pubDate: "2025-05-26"
updatedDate: '2026-09-12'
topics:
- "Discrete Logarithms"
- "Elliptic-Curve Cryptography"
- "Cryptanalysis"
- "Cryptographic Engineering"
tags:
- "bsgs"
- "baby-step-giant-step"
- "ecdlp"
- "shanks"
difficulty: "Advanced"
series: "Discrete Logarithm Algorithms"
seriesOrder: 2
sourcePath: "experiments/ready-material/discrete-log"
draft: false
---
#Discrete Log (Part 2): Baby-Step Giant-Step Algorithm (BSGS)

The **Baby-Step Giant-Step** algorithm is a classical method to solve the DLP efficiently in a finite cyclic group.

We refresh which is the actual problem that we want to solve: 

Let $G$ be a cyclic group of order $n$, and let $\alpha \in G$ be a generator. Given an element $\beta \in G$, the goal is to find an integer $x \in \{0, \dots, n-1\}$ such that:

$$
\alpha^x = \beta
$$

In the modular group setting:

$$
g^x \equiv h \mod p
$$


>The idea behing the BSGS algorithm precomputes a "baby step" table and then walks through "giant steps" to search for a collision. It relies on the time–memory tradeoff to reduce the complexity from linear to square-root time.

Below are the steps of the algorithm:

Let $n = \lceil \sqrt{N} \rceil$, where $N$ is the order of the group element $g$.

1. *Precomputation (Baby Steps)*

Create a table of the first $n$ powers of $g$:

$$
\text{Baby step list: } \quad \{(j, g^j) \mid 0 \leq j < n \}
$$

Store each pair $(j, g^j)$ in a hash map or dictionary for fast lookup.

2. *Compute Giant Step Factor*

Calculate the inverse power:

$$
g^{-n} \mod p \quad \text{(modular inverse exponentiation)}
$$

Set $\gamma = \beta$

3. *Giant Steps (Search Phase)*

For each $i = 0$ to $n-1$, do:

* Check if $\gamma$ is in the baby step table.
* If a match $g^j = \gamma$ is found, then:

   $$
   x = i \cdot n + j
   $$
* If no match, update:

   $$
   \gamma \leftarrow \gamma \cdot g^{-n} \mod p
   $$

Summarized we do the following:

Let:

* $g$ = generator of group $G$
* $h$ = target element
* $N$ = order of $g$
* $n = \lceil \sqrt{N} \rceil$

Then:

* **List 1 (Baby Steps)**: $\{g^0, g^1, \ldots, g^{n-1} \}$
* **List 2 (Giant Steps)**: $\{ h \cdot g^{-0n}, h \cdot g^{-1n}, \ldots, h \cdot g^{-n^2} \}$
* If a match occurs: $g^j = h \cdot g^{-in} \Rightarrow x = in + j$

BSGS is a square-root algorithm and significantly faster than brute-force for large groups with the following complexities: 

* **Time**: $\mathcal{O}(\sqrt{N})$
* **Space**: $\mathcal{O}(\sqrt{N})$

The whole conversation above was about the BSGS algorithm defined when the DLP is over a group. You can find a Python implementantion in `src/BSGSgroup.py`.  Below we present the analogous on the elliptic curve setting. 

## Baby-Step Giant-Step Algorithm for ECDLP


The *Elliptic Curve Discrete Logarithm Problem (ECDLP)* is a fundamental problem in elliptic curve cryptography (ECC). We refresh the problem: 


Given an elliptic curve $ E $ over a finite field and two points $ P $ and $ Q $, the problem is to determine the integer $ x $ such that:

$$
Q = xP
$$

This problem is computationally hard and forms the basis of ECC security. The (BSGS) algorithm for the ECDLP is an efficient algorithm that reduces the complexity of solving ECDLP from *exponential time* to *$ O(\sqrt{n}) $* using *space-time trade-off techniques*. We provide a SageMath implementation in `src/BSGSec.sage`. Below we explain briefly the code: 

### Function: **`bsgs_ecdlp(P, Q, E)`**
```python
import random

def bsgs_ecdlp(P, Q, E):
    if Q == E((0, 1, 0)):
        return P.order()
    if Q == P:
        return 1
```
- This function takes three parameters:
  - `P`: A generator point on the elliptic curve.
  - `Q`: The result of multiplying `P` by an unknown scalar `x`.
  - `E`: The elliptic curve.
- Base Cases:
  - If $ Q $ is the identity element *(point at infinity)*, return the *order of P*.
  - If $ Q = P $, return 1 because $ x = 1 \Rightarrow Q = 1P $.

### **Constructing the Lookup Table**
```python
    m = ceil(sqrt(P.order()))
    lookup_table = {j*P: j for j in range(m)}
```
- The algorithm sets *$ m = \lceil \sqrt{n} \rceil $*, where $ n $ is the order of the point $ P $.
- It *precomputes* a *lookup table* storing multiples of $ P $ up to $ m $:
  
  $$
  jP \quad \text{for} \quad j = 0,1,2, \dots, m-1
  $$
  
  This forms the *baby steps*.

### **Searching for the Solution**
```python
    for i in range(m):
        temp = Q - (i*m)*P
        if temp in lookup_table:
            return (i*m + lookup_table[temp]) % P.order()
```
- Iterates over $ i $ to compute the *giant steps*:
  
  $$
  Q - i m P
  $$
  
  - If this result exists in the *lookup table*, it means we have found a match:
    
    $$
    i m + j \equiv x \mod n
    $$
  
  - The algorithm then returns the recovered exponent $ x $.

The script includes a test block where we have defined the following EC parameters:  

```python
E = EllipticCurve(GF(17), [2, 2])
```
- Defines an elliptic curve over a finite field $\mathbb{GF}(17)$ with equation:
  
  $$
  y^2 = x^3 + 2x + 2 \mod 17
  $$

And we do the following test: 

```python
if __name__ == "__main__":
    E = EllipticCurve(GF(17), [2, 2])
    try:
        for i in range(100):
            x = random.randint(2, 19)
            assert bsgs_ecdlp(E((5, 1)), x*E((5, 1)), E) == x
    except Exception as e:
        print(e)
        print("[-] Something's wrong!")
```

We also have a randomized test, which tests the function 100 times by computing *$ Q = xP $* and checking if `bsgs_ecdlp(P, Q, E)` correctly recovers $x$, which is a random $x$ in the range $[2,19]$.

```python
for i in range(100):
    x = random.randint(2, 19)
    assert bsgs_ecdlp(E((5, 1)), x*E((5, 1)), E) == x
```

If the function fails, it prints:
```python
print("[-] Something's wrong!")
```

If everything works fine you should expect the following outputs: 

```
Test 1: x = 16, Computed x = 16, Q = (10 : 11 : 1)
Test 2: x = 8, Computed x = 8, Q = (13 : 7 : 1)
Test 3: x = 8, Computed x = 8, Q = (13 : 7 : 1)
Test 4: x = 10, Computed x = 10, Q = (7 : 11 : 1)
Test 5: x = 19, Computed x = 19, Q = (0 : 1 : 0)
Test 6: x = 13, Computed x = 13, Q = (16 : 4 : 1)
Test 7: x = 16, Computed x = 16, Q = (10 : 11 : 1)
Test 8: x = 9, Computed x = 9, Q = (7 : 6 : 1)
Test 9: x = 15, Computed x = 15, Q = (3 : 16 : 1)
Test 10: x = 17, Computed x = 17, Q = (6 : 14 : 1)
```

- In every case, the computed *x* matches the randomly selected *x*, confirming the *correctness of the algorithm*.
- In **Test #5**, $ Q = (0,1,0) $, which represents the *point at infinity*.
- This happens when *x = P.order()*, meaning the scalar was equal to the order of *P*.
- The algorithm finds *x* in significantly fewer steps than a naive brute force approach.
