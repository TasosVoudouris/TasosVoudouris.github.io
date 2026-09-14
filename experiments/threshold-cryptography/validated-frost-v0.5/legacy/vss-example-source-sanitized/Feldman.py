import random
from ecdsa import SigningKey, SECP256k1
from ecdsa.ellipticcurve import Point
from sympy import symbols, Poly

# Define the elliptic curve group (using secp256k1)
curve = SECP256k1
G = curve.generator
n = curve.order

# Generate keys for participants
def generate_keys(num_participants):
    private_keys = []
    public_keys = []
    for _ in range(num_participants):
        sk = SigningKey.generate(curve=SECP256k1)
        vk = sk.get_verifying_key()
        private_keys.append(sk)
        public_keys.append(vk)
    return private_keys, public_keys

# Create a random polynomial of degree t-1 with constant term s
def create_polynomial(s, t):
    x = symbols('x')
    coefficients = [s] + [random.randint(1, n-1) for _ in range(t-1)]
    poly = sum([coefficients[i] * x**i for i in range(t)])
    return Poly(poly, x), coefficients

# Evaluate polynomial at given points
def evaluate_polynomial(poly, points):
    return [int(poly.eval(point)) % n for point in points]

# Generate commitments for polynomial coefficients
def generate_commitments(coefficients):
    return [coeff * G for coeff in coefficients]

# Verify shares against commitments
def verify_share(share, commitments, alpha):
    x = symbols('x')
    commitment_point = commitments[0]
    for i in range(1, len(commitments)):
        commitment_point += commitments[i] * (alpha ** i % n)
    share_point = share * G
    return commitment_point == share_point

# Example usage
num_participants = 5  # Number of participants
threshold = 3  # Threshold to reconstruct the secret
secret = random.randint(1, n-1)

# Step 1: Generate keys
private_keys, public_keys = generate_keys(num_participants)

# Step 2: Create polynomial and generate shares
poly, coefficients = create_polynomial(secret, threshold)
alphas = [i + 1 for i in range(num_participants)]
shares = evaluate_polynomial(poly, alphas)

# Step 3: Generate commitments
commitments = generate_commitments(coefficients)

# Step 4: Verify shares against commitments
for i, (share, alpha) in enumerate(zip(shares, alphas)):
    valid = verify_share(share, commitments, alpha)
    print(f"Share {i+1} verification: {'Valid' if valid else 'Invalid'}")


print(commitments)