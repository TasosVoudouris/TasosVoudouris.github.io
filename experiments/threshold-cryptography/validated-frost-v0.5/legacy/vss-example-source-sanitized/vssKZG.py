import random
from sympy import symbols, Poly
from py_ecc import bn128 as b

# Define the elliptic curve group (using bn128)
n = b.curve_order

# Setup KZG commitment parameters
def setup_kzg(max_degree):
    secret = random.randint(1, n-1)
    powers_of_secret = [pow(secret, i, n) for i in range(max_degree + 1)]
    g1_powers = [b.multiply(b.G1, s) for s in powers_of_secret]
    g2_powers = [b.multiply(b.G2, s) for s in powers_of_secret]
    return g1_powers, g2_powers, secret

def create_polynomial(s, t):
    x = symbols('x')
    coefficients = [s] + [random.randint(1, n-1) for _ in range(t-1)]
    poly = sum([coefficients[i] * x**i for i in range(t)])
    return Poly(poly, x), coefficients

def evaluate_polynomial(poly, points):
    return [int(poly.eval(point)) % n for point in points]

def generate_kzg_commitments(coefficients, g1_powers):
    return [b.multiply(g1_powers[i], coefficients[i]) for i in range(len(coefficients))]

def verify_kzg_commitment(commitment, proof, alpha, g2_powers):
    lhs = b.pairing(commitment, b.G2)
    rhs = b.pairing(b.G1, proof) * b.pairing(b.multiply(b.G1, alpha), g2_powers[1])
    return lhs == rhs

def participant_work(num_participants, threshold, secret, g1_powers, g2_powers):
    poly, coefficients = create_polynomial(secret, threshold)
    alphas = [i + 1 for i in range(num_participants)]
    shares = evaluate_polynomial(poly, alphas)
    commitments = generate_kzg_commitments(coefficients, g1_powers)
    return shares, commitments, alphas
