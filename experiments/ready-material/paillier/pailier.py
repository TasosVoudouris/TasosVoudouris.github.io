import math
import random

def is_prime(x):
    for i in range(2, x):
        if x % i == 0:
            return False
    return True

p = 13
q = 17
assert p != q
assert is_prime(p)
assert is_prime(p)

n = p * q
phi = (p-1)*(q-1)

def lx(x):
    y = (x-1)/n
    assert y - int(y) == 0
    return int(y)

g = 1 + n
lmbda = phi * 1
mu = pow(phi, -1, n)

print(f"private key is lambda = {lmbda}. use this decryption.")
print(f"public key is g={g}, n={n}, mu={mu}. use this encryption.")

def encrypt(m, r):
    assert math.gcd(r, n) == 1
    c = ( pow(g, m, n*n) * pow(r, n, n*n) ) % (n*n)
    return c

def decrypt(c):
    p = ( lx(pow(c, lmbda, n*n)) * mu ) % (n)
    return p

m = 123
r = random.randint(0, n)

c = encrypt(m, r)
p = decrypt(c)

assert m == p

### additive homomorphic

m1 = 123
r1 = random.randint(0, n)

m2 = 37
r2 = random.randint(0, n)

c1 = encrypt(m1, r1)
c2 = encrypt(m2, r2)

assert ( c1 * c2 ) % (n*n) == encrypt(m1 + m2, r1*r2)


#### neutral element

m1 = 123
r1 = random.randint(0, n)

m2 = 0
r2 = random.randint(0, n)

c1 = encrypt(m1, r1)
c2 = encrypt(m2, r2)

c1_reencrypted = ( c1 * c2 ) % (n*n)

assert c1_reencrypted != c1

assert decrypt(c1_reencrypted) == decrypt(c1)

### homomorphic multiplication

m1 = 123
r1 = random.randint(0, n)

m2 = 25
r2 = random.randint(0, n)

c1 = encrypt(m1, r1)
c2 = encrypt(m2, r2)

assert pow(c1, m2, n*n) == encrypt(m1*m2, pow(r1, m2, n*n))
assert pow(c2, m1, n*n) == encrypt(m1*m2, pow(r2, m1, n*n))
assert decrypt(pow(c1, m2, n*n)) == (m1*m2) % n
assert decrypt(pow(c2, m1, n*n)) == (m1*m2) % n