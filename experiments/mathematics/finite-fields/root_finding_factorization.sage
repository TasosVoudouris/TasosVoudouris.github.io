### Rabin's algorithm of finding the rational roots of a polynomial

# Define a small prime field F_p and a polynomial ring R = F_p[x]
p = 61
F = GF(p)
R.<x> = PolynomialRing(F)
f = x^8 - 2*x + 5

# Print rational roots and factorization of f in F_p
print(f.roots())
print(f.factor())

# View roots in an extension field F_{p^6}
print(f.change_ring(GF(p^6)).roots())

# Check the fundamental identity over F_p: product of all linear terms = x^p - x
print(product([x - i for i in F]) == x^p - x)

# Check similar identity over F_{p^2}
print(product([x.change_ring(GF(p^2)) - i for i in GF(p^2)]) == x^(p^2) - x)

# Define the quotient ring R/(f)
pif = R.quotient(f)

# Define a large prime field and polynomial
p = 2^255 - 19
F = GF(p)
R.<x> = PolynomialRing(F)
f = x^8 - 2*x + 5
pif = R.quotient(f)

# Compute the polynomial with distinct rational roots
# This uses the identity gcd(f, x^q - x) where q = |F|
def distinct_root_poly(f):
    q = f.base_ring().cardinality()
    pif = f.parent().quotient(f)
    return gcd(f, (pif(x)^q).lift() - x)

def count_distinct_roots(f):
    return distinct_root_poly(f).degree()

# Count distinct roots of f over extension fields F_{p^n} for n = 1 to 6
p = 61
F = GF(p)
R.<x> = PolynomialRing(F)
f = x^8 - 2*x + 5
pif = R.quotient(f)
for n in range(1, 7):
    print("%d distinct roots over F_{%d^%d}" % (count_distinct_roots(f.change_ring(GF(p^n))), p, n))

# View the roots explicitly over F_p
print(gcd(f, (pif(x)^p - x).lift()))
s = (p - 1) // 2  # Half the size of multiplicative group, used for quadratic character test
print(gcd(f, (pif(x)^s - 1).lift()))

# Extract remaining roots
print(gcd(f, (pif(x)^p - x).lift()) / gcd(f, (pif(x)^s - 1).lift()))

# Check that x^s - 1 corresponds to squares in F_p^x
print(sorted((x^s - 1).roots()))
print(product([x - a^2 for a in F if a < p - a]) == (x^s - 1))

# Rabin's algorithm to find one rational root (probabilistically)
def rational_root(f):
    """Returns a rational root of f or None if f has no rational roots."""
    q = f.base_ring().cardinality()
    assert q % 2 == 1
    s = (q - 1) // 2
    x = f.parent().gen()
    if f[0] == 0:
        return f.base_ring()(0)
    g = distinct_root_poly(f)
    print("Initial g = gcd(f, x^q - x) = %s" % g)
    pig = g.parent().quotient(g)
    while g.degree() > 1:
        delta = g.base_ring().random_element()
        print("delta = %s" % delta)
        h = gcd(g, ((pig(x) - delta)^s - 1).lift())
        if 0 < h.degree() < g.degree():
            g = h if 2 * h.degree() <= g.degree() else g // h
            pig = g.parent().quotient(g)
            print("Better g = %s" % g)
    return -g[0] if g.degree() == 1 else None

# Find a rational root repeatedly (to observe the probabilistic behavior)
for i in range(5):
    r = rational_root(f)
    print("Found root %s\n" % r)
    assert f(r) == 0

# Test with a polynomial with known roots
h = product([x - i for i in range(1, 20)])
for i in range(5):
    r = rational_root(h)
    print("Found root %s\n" % r)
    assert h(r) == 0

# Test Rabin's algorithm with timing on a large field
p = 2^61 - 1
F = GF(p)
R.<x> = PolynomialRing(F)
f = x^8 - 2*x + 5
h = product([x - i for i in range(1, 20)])
for i in range(3):
    time print("Found root %s\n" % rational_root(h))

# Rabin's algorithm to find all distinct rational roots (recursively)
def distinct_rational_roots(f, recurse=False):
    """Returns a list of all the distinct rational roots of f."""
    q = f.base_ring().cardinality()
    assert q % 2 == 1
    s = (q - 1) // 2
    x = f.parent().gen()
    roots = []
    if recurse:
        g = f
    else:
        g = distinct_root_poly(f)
        if g(0) == 0:
            roots = [g.base_ring()(0)]
            g = g // x
    if g.degree() <= 1:
        return [-g[0]] if g.degree() == 1 else []
    while True:
        delta = g.base_ring().random_element()
        pig = g.parent().quotient(g)
        h = gcd(g, ((pig(x) - delta)^s - 1).lift())
        if 0 < h.degree() < g.degree():
            roots += distinct_rational_roots(h, True)
            roots += distinct_rational_roots(g // h, True)
            return roots

# Example use of distinct_rational_roots
print(distinct_rational_roots(f))
time distinct_rational_roots(f)
time distinct_rational_roots(product([x - F.random_element() for i in range(10)]))

# Yun's squarefree factorization algorithm
def squarefree_factorization(f):
    """Yun's algorithm to compute the squarefree factorization of a monic polynomial f in F_q[x].
    Returns list [1, g1, g2, ..., gm] such that f = g1 * g2^2 * ... * gm^m and gm ≠ 1.
    """
    assert f.degree() < f.base_ring().characteristic()
    if not f.is_monic:
        f = f.monic()
    df = f.derivative()
    u = gcd(f, df)
    v, w = f // u, df // u
    gs = [f.parent()(1)]
    while True:
        g = gcd(v, w - v.derivative())
        gs.append(g)
        if v.degree() == g.degree():
            return gs
        v, w = v // g, (w - v.derivative()) // g

# Rational root finder with multiplicities using squarefree factorization
def rational_roots(f):
    """Returns a list of tuples (a, m) where a is a rational root and m its multiplicity."""
    gs = squarefree_factorization(f)
    return reduce(lambda x, y: x + y,
                  [[(a, i) for a in distinct_rational_roots(gs[i])]
                   for i in range(1, len(gs))])

# Compute rational roots with multiplicities
h = product([(x - F.random_element())^i for i in range(1, 6)])
time rational_roots(h)

# GCD of f and x^{q^i} - x isolates irreducibles of degree i in f
def distinct_degree_poly(f, i):
    q = f.base_ring().cardinality()
    pif = f.parent().quotient(f)
    return gcd(f, (pif(x)^(q^i)).lift() - x)

# Distinct-degree factorization (optimized version)
def distinct_degree_factorization(f, squarefree=False):
    """
    Computes the distinct-degree factorization of f.
    Returns list gs with gs[0]=1 and gs[i] = product of all irreducible degree-i factors of f.
    If squarefree=True, skips squarefree check.
    """
    if not squarefree:
        return naive_distinct_degree_factorization(f)
    d = f.degree()
    gs = [f.parent()(1) for _ in range(d + 1)]
    for i in range(1, d + 1):
        if 2 * i > f.degree():
            gs[f.degree()] = f
            break
        gs[i] = distinct_degree_poly(f, i)
        f = f // gs[i]
    return gs

# Naive version to handle arbitrary f using squarefree factorization
def naive_distinct_degree_factorization(f):
    """Fallback method combining distinct-degree results across squarefree factors."""
    d = f.degree()
    gs = [f.parent()(1) for _ in range(d + 1)]
    hs = [distinct_degree_factorization(g, squarefree=True) for g in squarefree_factorization(f)]
    for i in range(1, len(hs)):
        for j in range(1, len(hs[i])):
            gs[j] *= hs[i][j]^i
    return gs

# Pattern of irreducible factors: maps degree -> count

def facpat(f):
    """Returns dictionary mapping degrees to counts of irreducible factors of that degree."""
    X = {}
    gs = squarefree_factorization(f)
    for i in range(1, len(gs)):
        gis = distinct_degree_factorization(gs[i], squarefree=True)
        for j in range(1, len(gis)):
            if gis[j].degree() > 0:
                X[j] = X.get(j, 0) + i * (gis[j].degree() // j)
    return X

# Cantor-Zassenhaus: equal-degree factorization for irreducible degree-j factors
def equal_degree_factorization(f, j):
    """Factors f into irreducibles of degree j assuming f is such a product."""
    d = f.degree()
    assert d % j == 0
    if d == 0:
        return []
    elif d == j:
        return [f]
    Fq = f.base_ring(); q = Fq.cardinality()
    assert q % 2 == 1
    s = (q^j - 1) // 2
    x = f.parent().gen()
    pif = f.parent().quotient(f)
    while True:
        u = f.parent()([Fq.random_element() for _ in range(d)])
        h = gcd(f, u)
        if 0 < h.degree() < d:
            return equal_degree_factorization(h, j) + equal_degree_factorization(f // h, j)
        h = gcd(f, (pif(u)^s - 1).lift())
        if 0 < h.degree() < d:
            return equal_degree_factorization(h, j) + equal_degree_factorization(f // h, j)

# Main Cantor-Zassenhaus factorization routine
def factorization(f):
    """Complete factorization of monic f in F_q[x] using Cantor-Zassenhaus (assumes q odd)."""
    assert f.degree() > 0
    if not f.is_monic:
        f = f.monic()
    res = []
    gs = squarefree_factorization(f)
    for i in range(1, len(gs)):
        gis = distinct_degree_factorization(gs[i], squarefree=True)
        for j in range(1, len(gis)):
            res += [(g, i) for g in equal_degree_factorization(gis[j], j)]
    return sorted(res)  # canonical ordering independent of randomness

assert factorization(f) == sorted(list(f.factor()))
print(factorization(f))

assert factorization(h) == sorted(list((h).factor()))
print(factorization(h))

p=2^255-19
F=GF(p); R.<x>=PolynomialRing(F)
f=x^8-2*x+5
h = product([x-i for i in range(1,20)])

assert factorization(f^3+f^2+1) == sorted(list((f^3+f^2+1).factor()))