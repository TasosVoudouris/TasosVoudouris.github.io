import random

Q = 41
N = 5

class Additive:
    
    def __init__(self, secret=None):
        self.secret = secret
        self.shares = self.additive_share(secret) if secret is not None else []
    
    def additive_share(self, secret):
        shares = [random.randrange(Q) for _ in range(N - 1)]
        shares.append((secret - sum(shares)) % Q)  # Ensuring the sum of shares equals the secret mod Q
        return shares

    def additive_reconstruct(self):
        return sum(self.shares) % Q
    
    def __add__(x, y):
        z = Additive()
        z.shares = [(xi + yi) % Q for xi, yi in zip(x.shares, y.shares)]
        return z

    def __sub__(x, y):
        z = Additive()
        z.shares = [(xi - yi) % Q for xi, yi in zip(x.shares, y.shares)]
        return z
    
    def reveal(self):
        return self.additive_reconstruct()

    def __repr__(self):
        return f"Additive({self.reveal()})"

# Main Code with changing secrets

# Random secret between 0 and Q-1
secret = random.randint(0, Q-1)

# Generate random shares and calculate the last share to make it sum to the secret
shares = [random.randrange(Q) for _ in range(N - 1)]
tenth_share = (secret - sum(shares)) % Q
shares.append(tenth_share)

# Print the results with the random secret and generated shares
print(f"Secret: {secret}")
print(f"Generated shares: {shares}")
print(f"Reconstructed secret from shares: {sum(shares) % Q}")

# Example of Additive secret sharing with random secrets
x_secret = random.randint(0, Q-1)
x = Additive(x_secret)
print(f"Shares for x (secret={x_secret}): {x.shares}")
print(f"Reconstructed secret for x: {x.reveal()}")

y_secret = random.randint(0, Q-1)
y = Additive(y_secret)
print(f"Shares for y (secret={y_secret}): {y.shares}")
print(f"Reconstructed secret for y: {y.reveal()}")

# Subtracting two secrets
z = x - y
print(f"Shares for z (x - y): {z.shares}")
print(f"Reconstructed secret for z: {z.reveal()} (should be {(x_secret - y_secret) % Q})")
assert z.reveal() == (x_secret - y_secret) % Q
