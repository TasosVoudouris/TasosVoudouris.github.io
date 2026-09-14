print("ElGamal Encryption")

# Generate a large prime number p
p = next_prime(2 ^ 100 + 8479783443)
print("p =", p)

# Create a finite field F with prime order p
F = GF(p)
# Choose a primitive root as the generator g
g = F(primitive_root(p))
print("Generator g =", g)

# Alice's private key (secret)
x = randrange(p)  
# Alice's public key y
y = g ^ x  
print("Alice: My private key is x =", x, "and my public key is y =", y)

# The message to be encrypted
m = randrange(p)
print("The message is m =", m)

# Bob's private key (one-time secret)
k = randrange(p - 1)  
# Bob's one-time public key a
a = g ^ k  
print("Bob: My one-time private key is k =", k, "and my public key is a =", a)

# Alice encrypts the message m using Bob's one-time public key
b = m * y ^ k  # y = g ^ x, so b = m * g ^ (xk)
print("Alice encrypts the message m as b =", b)

# Bob decrypts the message by computing the shared secret
c = a ^ x  # Compute the shared secret using Bob's one-time key and Alice's private key
print("Decryption result is", b / c)

# Explanation of decryption:
# b / c = (m * y ^ k) / (a ^ x) = (m * g ^ xk) / (g ^ kx) = m
