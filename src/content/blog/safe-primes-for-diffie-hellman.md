---
title: "Safe Primes and Subgroup Structure in Diffie–Hellman"
description: "A focused note on safe primes, subgroup order, generators, and why group structure matters when selecting finite-field Diffie–Hellman parameters."
pubDate: "2025-05-27"
updatedDate: '2026-09-12'
topics:
- "Number Theory"
- "Key Exchange"
- "Discrete Logarithms"
- "Public-Key Cryptography"
tags:
- "safe-primes"
- "sophie-germain-primes"
- "subgroups"
- "diffie-hellman"
difficulty: "Intermediate"
series: "Diffie–Hellman & ElGamal"
seriesOrder: 2
sourcePath: "experiments/ready-material/diffie-hellman"
draft: false
---
For Diffie Hellman and in general for cryptographic protocols we will want to have a large prime number $p$ **and** a primitive root mod $p$.  The easiest way to do this is to use a **Sophie Germain** prime $q$.  A Sophie Germain prime is a prime number $q$ such that $2q + 1$ is also prime.  When $q$ is a Sophie Germain prime, the resulting prime $p = 2q + 1$ is called a **safe prime**.

Observe that when $p$ is a safe prime, the prime decomposition of $p-1$ is 
$$p-1 = 2 \cdot q.$$
That's it.  So the possible multiplicative orders of an element $b$, mod $p$, are the divisors of $2q$, which are
$$1, 2, q, \text{ or } 2q.$$
In order to check whether $b$ is a primitive root, modulo a safe prime $p = 2q + 1$, we must check just three things:  is $b \equiv 1$, is $b^2 \equiv 1$, or is $b^q \equiv 1$, mod $p$?  If the answer to these three questions is NO, then $b$ is a primitive root mod $p$.

```python
def is_primroot_safe(b,p):
    '''
    Checks whether b is a primitive root modulo p,
    when p is a safe prime.  If p is not safe,
    the results will not be good!
    '''
    q = (p-1) // 2   # q is the Sophie Germain prime
    if b%p == 1:  # Is the multiplicative order 1?
        return False
    if (b*b)%p == 1:  # Is the multiplicative order 2?
        return False
    if pow(b,q,p) == 1:  # Is the multiplicative order q?
        return False
    return True  # If not, then b is a primitive root mod p.
```
   


This would not be very useful if we couldn't find Sophie Germain primes.  Fortunately, they are not so rare.  The first few are 2, 3, 5, 11, 23, 29, 41, 53, 83, 89.  It is expected, but unproven that there are infinitely many Sophie Germain primes.  In practice, they occur fairly often.  If we consider numbers of magnitude $N$, about $1 / \log(N)$ of them are prime.  Among such primes, we expect about $1.3 / \log(N)$ to be Sophie Germain primes.  In this way, we can expect to stumble upon Sophie Germain primes if we search for a bit (and if $\log(N)^2$ is not too large).

The code below tests whether a number $p$ is a Sophie Germain prime.  We construct it by simply testing whether $p$ and $2p+1$ are both prime.  We use the Miller-Rabin test in order to test whether each is prime.
from random import randint # randint chooses random integers.

```python
def Miller_Rabin(p, base):
    '''
    Tests whether p is prime, using the given base.
    The result False implies that p is definitely not prime.
    The result True implies that p **might** be prime.
    It is not a perfect test!
    '''
    result = 1
    exponent = p-1
    modulus = p
    bitstring = bin(exponent)[2:] # Chop off the '0b' part of the binary expansion of exponent
    for bit in bitstring: # Iterates through the "letters" of the string.  Here the letters are '0' or '1'.
        sq_result = result*result % modulus  # We need to compute this in any case.
        if sq_result == 1:
            if (result != 1) and (result != exponent):  # Note that exponent is congruent to -1, mod p.
                return False  # a ROO violation occurred, so p is not prime
        if bit == '0':
            result = sq_result 
        if bit == '1':
            result = (sq_result * base) % modulus
    if result != 1:
        return False  # a FLT violation occurred, so p is not prime.
    
    return True  # If we made it this far, no violation occurred and p might be prime.

def is_prime(p, witnesses=50):  # witnesses is a parameter with a default value.
    '''
    Tests whether a positive integer p is prime.
    For p < 2^64, the test is deterministic, using known good witnesses.
    Good witnesses come from a table at Wikipedia's article on the Miller-Rabin test,
    based on research by Pomerance, Selfridge and Wagstaff, Jaeschke, Jiang and Deng.
    For larger p, a number (by default, 50) of witnesses are chosen at random.
    '''
    if (p%2 == 0): # Might as well take care of even numbers at the outset!
        if p == 2:
            return True
        else:
            return False 
    
    if p > 2**64:  # We use the probabilistic test for large p.
        trial = 0
        while trial < witnesses:
            trial = trial + 1
            witness = randint(2,p-2) # A good range for possible witnesses
            if Miller_Rabin(p,witness) == False:
                return False
        return True
    
    else:  # We use a determinisic test for p <= 2**64.
        verdict = Miller_Rabin(p,2)
        if p < 2047:
            return verdict # The witness 2 suffices.
        verdict = verdict and Miller_Rabin(p,3)
        if p < 1373653:
            return verdict # The witnesses 2 and 3 suffice.
        verdict = verdict and Miller_Rabin(p,5)
        if p < 25326001:
            return verdict # The witnesses 2,3,5 suffice.
        verdict = verdict and Miller_Rabin(p,7)
        if p < 3215031751:
            return verdict # The witnesses 2,3,5,7 suffice.
        verdict = verdict and Miller_Rabin(p,11)
        if p < 2152302898747:
            return verdict # The witnesses 2,3,5,7,11 suffice.
        verdict = verdict and Miller_Rabin(p,13)
        if p < 3474749660383:
            return verdict # The witnesses 2,3,5,7,11,13 suffice.
        verdict = verdict and Miller_Rabin(p,17)
        if p < 341550071728321:
            return verdict # The witnesses 2,3,5,7,11,17 suffice.
        verdict = verdict and Miller_Rabin(p,19) and Miller_Rabin(p,23)
        if p < 3825123056546413051:
            return verdict # The witnesses 2,3,5,7,11,17,19,23 suffice.
        verdict = verdict and Miller_Rabin(p,29) and Miller_Rabin(p,31) and Miller_Rabin(p,37)
        return verdict # The witnesses 2,3,5,7,11,17,19,23,29,31,37 suffice for testing up to 2^64. 
    
def is_SGprime(p):
    '''
    Tests whether p is a Sophie Germain prime
    '''
    if is_prime(p):  # A bit faster to check whether p is prime first.
        if is_prime(2*p + 1):  # and *then* check whether 2p+1 is prime.
            return True
    return False
```

Let's test this out by finding the Sophie Germain primes up to 100, and their associated safe primes.
```python
for j in range(1,100):
    if is_SGprime(j):
        print(j, 2*j+1)
```
Next, we find the first 100-digit Sophie Germain prime!  This might take a minute!
```python
test_number = 10**99 # Start looking at the first 100-digit number, which is 10^99.
while not is_SGprime(test_number):
    test_number = test_number + 1
print(test_number)
```
