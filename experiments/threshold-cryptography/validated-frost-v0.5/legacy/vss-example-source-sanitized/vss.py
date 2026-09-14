import random
from ecdsa import SigningKey, SECP256k1
from sympy import symbols, Poly
from ecdsa.ellipticcurve import Point, INFINITY

# Define the elliptic curve group (using secp256k1)
curve = SECP256k1
G = curve.generator
n = curve.order

def generate_keys(num_participants):
    private_keys = []
    public_keys = []
    for _ in range(num_participants):
        sk = SigningKey.generate(curve=SECP256k1)
        vk = sk.get_verifying_key()
        private_keys.append(sk)
        public_keys.append(vk)
    return private_keys, public_keys

def create_polynomial(s, t):
    x = symbols('x')
    coefficients = [s] + [random.randint(1, n-1) for _ in range(t-1)]
    poly = sum([coefficients[i] * x**i for i in range(t)])
    return Poly(poly, x), coefficients

def evaluate_polynomial(poly, points):
    return [int(poly.eval(point)) % n for point in points]

def generate_commitments(coefficients):
    return [coeff * G for coeff in coefficients]

def verify_share(share, commitments, alpha):
    commitment_point = commitments[0]
    for i in range(1, len(commitments)):
        commitment_point += commitments[i] * (alpha ** i % n)
    share_point = share * G
    return commitment_point == share_point

def participant_work(num_participants, threshold, secret):
    poly, coefficients = create_polynomial(secret, threshold)
    alphas = [i + 1 for i in range(num_participants)]
    shares = evaluate_polynomial(poly, alphas)
    commitments = generate_commitments(coefficients)
    return shares, commitments, alphas

def reconstruct_secret(shares, alphas, threshold):
    x = symbols('x')
    lagrange_basis = []
    for i in range(threshold):
        numer = 1
        denom = 1
        for j in range(threshold):
            if i != j:
                numer *= (x - alphas[j])
                denom *= (alphas[i] - alphas[j])
        lagrange_basis.append(numer / denom)
    secret = 0
    for i in range(threshold):
        secret += shares[i] * lagrange_basis[i]
    secret = secret.evalf(subs={x: 0})
    return int(secret % n)

# Serialization and deserialization functions
def serialize_point(point):
    if point == INFINITY:
        return 'infinity'
    x, y = point.x(), point.y()
    return f'{x},{y}'

def deserialize_point(data):
    if data == 'infinity':
        return INFINITY
    x, y = map(int, data.split(','))
    return Point(curve.curve, x, y)
