import random
from sympy import isprime, mod_inverse

# Function to generate a random prime number
def generate_prime(candidate=1):
    while not isprime(candidate):
        candidate += 1
    return candidate

# Function to generate key pairs
def generate_keys():
    # Choose two distinct prime numbers p and q (small primes for simplicity)
    p = generate_prime(random.randint(100, 200))
    q = generate_prime(random.randint(100, 200))
    
    # Compute n = pq and Euler's totient function phi(n) = (p-1)(q-1)
    n = p * q
    phi = (p - 1) * (q - 1)
    
    # Choose an integer e such that 1 < e < phi(n) and gcd(e, phi(n)) = 1
    e = random.randint(2, phi - 1)
    while mod_inverse(e, phi) is None:
        e = random.randint(2, phi - 1)
    
    # Compute d such that ed ≡ 1 (mod phi(n))
    d = mod_inverse(e, phi)
    
    # Public key (e, n) and private key (d, n)
    return ((e, n), (d, n))

# Function to encrypt a message
def encrypt(message, pub_key):
    e, n = pub_key
    return [pow(ord(char), e, n) for char in message]

# Function to decrypt a message
def decrypt(ciphertext, priv_key):
    d, n = priv_key
    return ''.join([chr(pow(char, d, n)) for char in ciphertext])

# Main function to demonstrate RSA
def main():
    # Generate public and private keys
    public_key, private_key = generate_keys()
    
    # Print keys
    print(f"Public Key: {public_key}")
    print(f"Private Key: {private_key}")
    
    # Original message
    message = "Crypto is fun when you know maths"
    print(f"Original Message: {message}")
    
    # Encrypt the message
    encrypted_message = encrypt(message, public_key)
    print(f"Encrypted Message: {encrypted_message}")
    
    # Decrypt the message
    decrypted_message = decrypt(encrypted_message, private_key)
    print(f"Decrypted Message: {decrypted_message}")

# Run the main function
if __name__ == "__main__":
    main()
