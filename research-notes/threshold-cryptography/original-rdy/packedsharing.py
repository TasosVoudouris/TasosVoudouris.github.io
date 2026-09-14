import random

# Define the modulus and parameters
Q = 101 # Modulus for modular arithmetic
N = 20  # Number of total shares
T = 8   # Number of random points
K = 5   # Number of secrets to pack

assert(T + K <= N)


############### ENCODING ############

def encode(x):
    return x % Q

def decode(x):
    return x if x <= Q/2 else x-Q


# Function to evaluate a polynomial at a given point using Horner's rule
def evaluate_at_point(coefs, point):
    result = 0
    for coef in reversed(coefs):
        result = (coef + point * result) % Q
    return result

# Extended Euclidean Algorithm (to calculate modular inverses)
def egcd(a, b):
    if a == 0:
        return (b, 0, 1)
    else:
        g, y, x = egcd(b % a, a)
        return (g, x - (b // a) * y, y)

# Inverse function using Extended Euclidean Algorithm in binary form
def inverse(a):
    _, b, _ = egcd(a, Q)
    return b % Q

# Lagrange interpolation to calculate  Lagrange constants (Li) at a given point
def lagrange_constants_for_point(points, point):
    constants = [0] * len(points)
    for i in range(len(points)):
        xi = points[i]
        num = 1
        denum = 1
        for j in range(len(points)):
            if j != i:
                xj = points[j]
                num = (num * (xj - point)) % Q
                denum = (denum * (xj - xi)) % Q
        constants[i] = (num * inverse(denum)) % Q
    return constants

# Interpolating the polynomial at a specific point using Lagrange constants
def interpolate_at_point(points_values, point):
    points, values = zip(*points_values)
    constants = lagrange_constants_for_point(points, point)
    return sum(vi * ci for vi, ci in zip(values, constants)) % Q

# Secret and Randomness Points
SECRET_POINTS = [-p % Q for p in range(1, K + 1)]
RANDOMNESS_POINTS = [-p % Q for p in range(K + 1, K + T + 1)]
assert(set(SECRET_POINTS).intersection(RANDOMNESS_POINTS) == set())

# Sample polynomial with secrets and random coefficients
def sample_packed_polynomial(secrets):
    assert len(secrets) == K
    points = SECRET_POINTS + RANDOMNESS_POINTS
    values = secrets + [random.randrange(Q) for _ in range(T)]
    print(f"Polynomial points (Secret + Randomness): {list(zip(points, values))}")
    return list(zip(points, values))

# Share points for distribution
SHARE_POINTS = [p for p in range(1, N + 1)]
assert(set(SHARE_POINTS).intersection(SECRET_POINTS) == set())
assert(set(SHARE_POINTS).intersection(RANDOMNESS_POINTS) == set())

# Function to generate shares for a set of secrets
def packed_share(secrets):
    polynomial = sample_packed_polynomial(secrets)
    shares = [interpolate_at_point(polynomial, p) for p in SHARE_POINTS]
    print(f"Shares generated: {shares}")
    return shares

# Function to reconstruct secrets from shares
def packed_reconstruct(shares):
    polynomial = [(p, v) for p, v in zip(SHARE_POINTS, shares) if v is not None]
    secrets = [interpolate_at_point(polynomial, p) for p in SECRET_POINTS]
    return secrets

# Example secrets to pack and share
secrets = [5,6, 4, 3, 10]  # five secrets
print(f"Original secrets: {secrets}")

# Generate shares for the secrets
shares = packed_share(secrets)

# Corrupt some shares for testing (optional)
for i in range(N - (T + K)):
    shares[i] = None  # Simulate missing shares
print(f"CURRENT SHARES: {shares}")

# Reconstruct the secrets
reconstructed_secrets = packed_reconstruct(shares)
print(f"Reconstructed secrets: {reconstructed_secrets}")

# Ensure the reconstruction matches the original secrets
assert reconstructed_secrets == secrets, "Reconstructed secrets do not match the original!"


def packed_add(x, y):
    return [ (xi + yi) % Q for xi, yi in zip(x, y) ]

def packed_sub(x, y):
    return [ (xi - yi) % Q for xi, yi in zip(x, y) ]


def packed_mul(x, y):
    return [ (xi * yi) % Q for xi, yi in zip(x, y) ]

class Packed:
    def __init__(self, secrets, N=20, T=8, Q=41):
        self.Q = Q
        self.N = N
        self.K = len(secrets)
        self.T = T
        assert self.K + self.T <= self.N, "Need T+K ≤ N"
        # recompute all of the points from self.K, self.T, self.Q:
        self.secret_pts = [(-i) % Q for i in range(1, self.K+1)]
        self.rand_pts   = [(-i) % Q for i in range(self.K+1, self.K+self.T+1)]
        self.share_pts  = list(range(1, N+1))
        # sample and interpolate exactly as before, but passing self.* everywhere:
        polynomial = list(zip(
            self.secret_pts + self.rand_pts,
            [encode(s) for s in secrets] + [random.randrange(Q) for _ in range(self.T)]
        ))
        self.shares = [ interpolate_at_point(polynomial, p) for p in self.share_pts ]
        self.degree = self.K + self.T - 1

    def reveal(self):
        available = [(p,v) for p,v in zip(self.share_pts,self.shares) if v is not None]
        recovered = [interpolate_at_point(available, p) for p in self.secret_pts]
        return [ decode(r) for r in recovered ]

    def __repr__(self):
        return f"Packed({self.reveal()})"

    def __add__(self, other):
        assert (self.N, self.K, self.Q) == (other.N, other.K, other.Q)
        z = Packed.__new__(Packed)
        # copy parameters
        z.N, z.K, z.T, z.Q = self.N, self.K, self.T, self.Q
        z.secret_pts, z.rand_pts, z.share_pts = self.secret_pts, self.rand_pts, self.share_pts
        # component‐wise add
        z.shares = [ (a+b) % self.Q for a,b in zip(self.shares, other.shares) ]
        z.degree = max(self.degree, other.degree)
        return z

    def __mul__(self, other):
        assert (self.N, self.K, self.Q) == (other.N, other.K, other.Q)
        z = Packed.__new__(Packed)
        z.N, z.K, z.Q = self.N, self.K, self.Q
        # after multiplication the degree is the sum
        z.degree = self.degree + other.degree
        # keep the same point‐sets
        z.secret_pts, z.rand_pts, z.share_pts = self.secret_pts, self.rand_pts, self.share_pts
        z.shares = [ (a*b) % self.Q for a,b in zip(self.shares, other.shares) ]
        return z

# create two packed objects over the same parameters
x = Packed([1,2,3,4,5], N=30, T=10, Q=101)
y = Packed([5,9,10,11,5], N=30, T=10, Q=101)

# homomorphic addition
z_add = x + y
print("x + y =", z_add)                
assert z_add.reveal() == [ (a+b) % 101
                           for a,b in zip([1,2,3,4,5], [5,9,10,11,5]) ]

# homomorphic multiplication
z_mul = x * y
print("x * y =", z_mul)
assert z_mul.reveal() == [ (a*b) % 101
                           for a,b in zip([1,2,3,4,5], [5,9,10,11,5]) ]

print("Addition and multiplication tests passed!")


