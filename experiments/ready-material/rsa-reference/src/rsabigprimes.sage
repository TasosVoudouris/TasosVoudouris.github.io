
### RSA cryptosystem #####


# p, q : Choose 2 prime numbers
# random_prime(2 ^ 32)
p = 1934720747213161123444005428327792833507231547135206223715331967523648393068534557850212140122551667934011233803718412153
print("p = ", p)
# random_prime(2 ^ 32)
q = 214962810512734861918545003841883228687974884177284802562476682581869712567333319742749643778039531875355054721512057259
print("q = ", q)

# N: Encryption modulo
N = p * q
print("N = ", N)

# phi: Indicator value Euler
phi = (p - 1) * (q - 1)
# phi = euler_phi(N) # Same calculation
print("phi(N) = ", phi)

# e: Encryption exponent
# Search e until e is prime with phi
e = ZZ.random_element(phi)
while gcd(e, phi) != 1:
    print("\t-", e, "not prime with ", phi)
    e = ZZ.random_element(phi)
e = 65537
print("public exponent e = ", e)

# d: Decryption exponent
# d is the inverse of e mod phi(N) (Extended Euclidean algorithm)
d = ZZ(1 / Mod(e, phi))

print("Secret exponent d =", d)
print("d * e mod phi = ", Mod(d * e, phi))
print("public key (n, e) = (", N, ",", e,
      "); private key (d) = (", d, ")\n")

# Encryption/Decryption
# Select a message
m = randrange(N)
print("message m = ", m)

# Message encryption
c = power_mod(m, e, N)
print("encryption(m): c = m ^ e mod N =", c)

# Message decryption
m = power_mod(c, d, N)  # should be m again
print("decryption(c): m = c ^ d mod N =", m, "\n")

# Signature
# Select a message
m = randrange(N)
print("message m = ", m)

# Sign
s = power_mod(m, d, N)
print("Signature(m): s = m ^ d mod N =", s)

# Verify
m = power_mod(s, e, N)
print("Check(s): m = s ^ e mod N =", m)