---
title: "Discrete Logarithms IV: Pollard’s Rho for ECDLP"
description: "A detailed exploration of Pollard’s rho method for elliptic-curve discrete logarithms, including partitions, random walks, collision equations, and implementation."
pubDate: "2025-05-26"
updatedDate: '2026-09-12'
topics:
- "Discrete Logarithms"
- "Elliptic-Curve Cryptography"
- "Cryptanalysis"
- "Cryptographic Engineering"
tags:
- "pollard-rho"
- "ecdlp"
- "random-walk"
- "collision-search"
difficulty: "Advanced"
series: "Discrete Logarithm Algorithms"
seriesOrder: 4
sourcePath: "experiments/ready-material/discrete-log"
draft: false
---
Pollard’s Rho elliptic curve variant algorithm is a randomized method designed to solve the DLP. We trying to solve: 

$$Q = kP$$

where:

* $P$ is a known generator point on an elliptic curve,
* $Q$ is a point obtained by scalar multiplication of $P$, and
* $k$ is the unknown discrete logarithm we wish to compute.

Pollard’s Rho provides an effective solution when the group order is small enough or poorly chosen.


Let $E$ be an elliptic curve over a finite field $\mathbb{F}_p$ with a cyclic subgroup of prime order $n$. We assume a generator $P \in E(\mathbb{F}_p)$ and another point $Q = kP$. The Pollard’s Rho method relies on:

* *Random walks* in the group.
* *Cycle detection*, particularly using Floyd’s algorithm.
* The *birthday paradox*, which implies that collisions are expected in $O(\sqrt{n})$ steps.

By detecting a collision between two pseudorandom sequences generated over the group, we obtain a congruence relation that can be solved for $k$.

Below we explain the algorithm in more detail. A SageMath implementantion can be found in `src/rhoEC.sage`.

The algorithm has the following inputs:

* Elliptic curve $E$ over $\mathbb{F}_p$
* Generator point $P \in E(\mathbb{F}_p)$
* Target point $Q = kP$

And it provides an integer $k$ such that $Q = kP$, as an output. 

## The core
We first define our finite field and elliptic curve using random (or fixed) parameters:

```python
# SageMath code
p = 1035418103

# Choose valid curve parameters a, b such that 4a^3 + 27b^2 ≠ 0
while True:
    a = randint(1, p)
    b = randint(1, p)
    if (4*a^3 + 27*b^2) % p != 0:
        break

F = GF(p)
E = EllipticCurve(F, [a, b])
```

We ensure the elliptic curve is *non-singular* by checking the discriminant condition $4a^3 + 27b^2 \neq 0 \mod p$. This guarantees that the curve forms a valid group structure.

You may replace the random values with fixed ones for repeatability, like below: 
```python
# Overwriting the values with fixed parameters
prime = 1035418103
var_a = 45181635
var_b = 124806060

E = EllipticCurve(GF(prime), [1, 0, 0, var_a, var_b])
P = E.gen(0)
print('P: %s, n: %d' % (P, P.order()))
```

Once the curve is defined, the next steps involve selecting a generator $P \in E$ and computing a target point $Q = kP$ for some hidden $k$. The main loop then simulates the random walk and detects a collision. From that, $k$ is recovered using modular arithmetic.


### Hash-Based Partitioning of the Elliptic Curve Group

To define a pseudorandom walk over the elliptic curve group $E(\mathbb{F}_p)$, we partition the group into a fixed number of subsets using a hash function. This helps introduce *structured randomness* into the walk and is essential to simulate uniform behavior across the group.

We define the partitioning function as follows:

```python
def hash_function(point):
    bytes = struct.pack('f'*len(point), *point)
    return hashlib.md5(bytes).hexdigest()

def get_set(P, number_of_sets):
    hashdigest = hash_function(P)
    hash_as_int = int(hashdigest, 16)
    return 1 + (hash_as_int % number_of_sets)
```

* The `hash_function(point)` converts the coordinates of a point $P = (x, y) \in E(\mathbb{F}_p)$ into a byte sequence and hashes it using MD5.
* The function `get_set(P, number_of_sets)` then maps each point to one of the `number_of_sets` using a modulo operation.
* For this implementation, we typically use `number_of_sets = 3`, corresponding to three group actions:

  * *Addition of $P$*: simulates linear progress.
  * *Doubling of point*: accelerates growth and maintains cyclicity.
  * *Addition of $Q$*: injects the unknown into the walk and aids in building the relation needed to solve the DLP.

This hashing mechanism underlies the core idea of *partitioning*, enabling the Pollard's Rho algorithm to explore the group efficiently and detect a collision within $O(\sqrt{n})$ steps.


The core of Pollard’s Rho lies in simulating a pseudorandom walk over the group $E(\mathbb{F}_p)$. This is achieved by recursively updating a current state $R_i = a_i P + b_i Q$ according to the deterministic rule guided by the hash-based partitioning we mentioned above. Each step in the walk must maintain knowledge of how the point was constructed from $P$ and $Q$ to eventually solve for the discrete logarithm.

### Random walks

Below we present the steps of the algorithm for the random walks: 


We partition the group into three subsets $S_1, S_2, S_3$, and define an iteration function depending on the subset.

* Compute the Next Point in the Random Walk:

```python
def get_nextR(P, Q, R):
    if get_set(R, 3) == 1:
        nextR = Q + R
    elif get_set(R, 3) == 2:
        nextR = 2 * R
    elif get_set(R, 3) == 3:
        nextR = P + R
    return nextR
```

This function computes the *next point* $R_{i+1}$ in the sequence, based on the set to which the current point $R_i$ belongs.

* If $R \in S_1$: Set $R \leftarrow R + P$, update counters accordingly
* If $R \in S_2$: Set $R \leftarrow 2R$, update counters accordingly
* If $R \in S_3$: Set $R \leftarrow R + Q$, update counters accordingly

This ensures that the walk introduces *non-linear and unpredictable behavior* while still being deterministic and invertible, enabling the possibility of collision detection.

Then we have to update the coefficients $(a_i, b_i)$: 

```python
def get_next_a_and_b(P, Q, a, b):
    n = P.order()
    R = a * P + b * Q
    
    if get_set(R, 3) == 1:
        next_a = a
        next_b = b + 1
    elif get_set(R, 3) == 2:
        next_a = 2 * a % n
        next_b = 2 * b % n
    elif get_set(R, 3) == 3:
        next_a = a + 1
        next_b = b
    return next_a, next_b
```

Each point $R_i$ in the walk is associated with coefficients $a_i$ and $b_i$ such that:

$$
R_i = a_i P + b_i Q
$$

This function ensures we correctly track how $R_i$ evolves from the initial seed values, which is crucial for solving the linear congruence:

$$
(a_i - a_j)P = (b_j - b_i)Q \Rightarrow k \equiv \frac{a_i - a_j}{b_j - b_i} \mod n
$$

assuming the denominator is invertible modulo $n$.


The final step is to bring all components together to solve the equation $Q = kP$ by detecting a collision in the pseudorandom walk and solving the resulting congruence.

```python
def pollards_rho_algorithm(P, Q):
    R = P
    a = 1
    b = 0
    
    # Initialize tortoise (R1) and hare (R2) for cycle detection
    R1 = get_nextR(P, Q, R)
    R2 = get_nextR(P, Q, R1)
    
    a1, b1 = get_next_a_and_b(P, Q, a, b)
    a2, b2 = get_next_a_and_b(P, Q, a1, b1)
    
    # Iterate until collision is found
    while True:
        R1 = get_nextR(P, Q, R1)  # Single step
        R2 = get_nextR(P, Q, get_nextR(P, Q, R2))  # Double step
        
        a1, b1 = get_next_a_and_b(P, Q, a1, b1)
        a, b = get_next_a_and_b(P, Q, a2, b2)
        a2, b2 = get_next_a_and_b(P, Q, a, b)
        
        if R1 == R2:
            break
    
    # Collision found: R1 = R2 => a1*P + b1*Q = a2*P + b2*Q
    # Solve (a2 - a1)P = (b1 - b2)Q => k ≡ (a2 - a1)/(b1 - b2) mod n
    diff_a = a2 - a1
    diff_b = b1 - b2

    return (diff_a / diff_b) % P.order()
```

1. **Cycle Detection**:  
   * The function implements *Floyd’s cycle-finding algorithm*, using two pointers (`R1` and `R2`), one moving at double speed.
   * Once they collide, it implies that the internal state (i.e., the point $R_i$) has entered a cycle, allowing for the recovery of a linear relation.

2. **Modular Congruence from Collision**:

   * A collision $R_1 = R_2$ gives:

     $$
     a_1 P + b_1 Q = a_2 P + b_2 Q \Rightarrow (a_2 - a_1)P = (b_1 - b_2)Q
     $$
   * This implies:

     $$
     k \equiv \frac{a_2 - a_1}{b_1 - b_2} \mod n
     $$

     where $n = \text{order}(P)$, and we assume $b_1 \neq b_2$ and $\gcd(b_1 - b_2, n) = 1$, so that division modulo $n$ is well-defined.

3. **Efficiency**:

   * The expected runtime is $O(\sqrt{n})$ due to the *birthday paradox*, making this algorithm efficient in smaller cyclic subgroups.


To test the implementation and validate correctness, we simulate a challenge of recovering a randomly generated discrete logarithm $k$ such that $Q = kP$:

```python
k = random.randint(0, prime)
Q = k * P

print('k: %d, Q: %s' % (k, Q))
start_timestamp = current_milli_time()
x = pollards_rho_algorithm(P, Q)
end_timestamp = current_milli_time()

print('Time elapsed', end_timestamp - start_timestamp)
print('Solution: %s, Collision successful? %s' % (x, x * P == Q))
```


* A random scalar $k \in [0, p-1]$ is selected.
* The corresponding point $Q = kP$ is computed on the elliptic curve.
* The algorithm attempts to recover $k$ from the known $P$ and $Q$.
* The correctness is verified by checking if $xP = Q$.

This empirical test confirms that the algorithm is able to reverse scalar multiplication under appropriate assumptions, demonstrating its utility for both cryptanalysis and algorithmic pedagogy.


So to summarize, the *Pollard’s Rho algorithm* for the elliptic curve discrete logarithm problem (ECDLP) is a powerful and elegant method leveraging:

* *Random walks* guided by hashed partitions of group elements,
* *Cycle detection* via the Floyd’s “tortoise and hare” technique,
* And *modular arithmetic* to recover discrete logarithms from collisions.

Its expected time complexity is $O(\sqrt{n})$, where $n$ is the order of the group, making it one of the most efficient generic attacks on ECDLP for small- to medium-sized curve groups. This underscores the importance of choosing *strong cryptographic parameters*, especially large prime-order groups, to mitigate the feasibility of such attacks.
