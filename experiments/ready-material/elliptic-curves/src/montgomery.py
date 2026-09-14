from Crypto.Util.number import inverse
from ecdsa.ellipticcurve import CurveFp, Point

def legendre(a, p):
    return pow(a, (p - 1) // 2, p)
 
def tonelli(n, p):
    assert legendre(n, p) == 1, "not a square (mod p)"
    q = p - 1
    s = 0
    while q % 2 == 0:
        q //= 2
        s += 1
    if s == 1:
        return pow(n, (p + 1) // 4, p)
    for z in range(2, p):
        if p - 1 == legendre(z, p):
            break
    c = pow(z, q, p)
    r = pow(n, (q + 1) // 2, p)
    t = pow(n, q, p)
    m = s
    t2 = 0
    while (t - 1) % p != 0:
        t2 = (t * t) % p
        for i in range(1, m):
            if (t2 - 1) % p == 0:
                break
            t2 = (t2 * t2) % p
        b = pow(c, 1 << (m - i - 1), p)
        r = (r * b) % p
        c = (b * b) % p
        t = (t * c) % p
        m = i
    return r

def is_on(P, C):
    """
    Checks if a point P is on the montgomery curve C
    """
    A, B, p = C
    x, y = P
    return (B* y**2) % p == (x**3 + A * x**2 + x) % p


def lift(x, C):
    """
    Lifts a coordinate `x` to a point on the curve `C` if possible
    """
    A, B, p = C
    y = tonelli((x**3 + A * x**2 + x) % p, p)
    return (x, y)

def montgomery_addition(P1, P2, C):
    """
    Adds 2 points P1, P2 on the curve C
    """
    
    assert(is_on(P1, C)), f"The point {P1} is not on curve {C}"
    assert(is_on(P2, C)), f"The point {P2} is not on curve {C}"
    
    A, B, p = C
    x1, y1 = P1
    x2, y2 = P2
    
    #assert(x1 != x2 and y1 != y2), "P must not be equal to Q"
    lam = ((y2 - y1) * inverse(x2 - x1, p)) % p
    x3 = (B * lam ** 2 - A - x1 - x2) % p
    y3 = (lam * (x1 - x3) - y1) % p
    
    return (x3, y3)

def montgomery_doubling(P, C):
    """
    Double a point P on the curve C
    """
    
    assert(is_on(P, C)), f"The point {P} is not on curve {C}"
    
    A, B, p = C
    x, y = P
    
    lam = ((3*x**2 + 2*A*x + 1) * inverse(2 * B * y, p)) % p
    x3 = (B * lam ** 2 - A - 2 * x) % p
    y3 = (lam * (x - x3) - y) % p
    
    return (x3, y3)

def montgomery_binary(P, k, C):
    """
    Return k*P on C given P, k, C
    """
    assert(is_on(P, C)), f"The point {P} is not on curve {C}"

    R0 = P
    R1 = montgomery_doubling(P, C)
    l = k.bit_length()
    assert((k >> (l-1)) & 1 == 1), "the l-bit k must have the l-1 bit equal to 1"
    for i in range(l-2, -1, -1):
        if (k>>i) & 1 == 0:
            R0, R1= montgomery_doubling(R0, C), montgomery_addition(R0, R1, C)
        else:
            R0, R1= montgomery_addition(R0, R1, C), montgomery_doubling(R1, C)
    
    return R0

def is_on_w(P, C):
    """
    Checks if a point P is on the Weierstrass curve C
    """
    a, b, p = C
    x, y = P
    return y**2 % p == (x**3 + a * x + b) % p

def montgomery_to_weierstrass_curve(C):
    """
    Returns the weierstrass form curve from a given Montgomery curve
    """
    A, B, p = C
    
    a = ((3 - A**2) * inverse(3 * B ** 2, p)) % p
    b = ((2 * A**3 - 9*A) * inverse(27 * B**3, p)) % p
    
    return (a, b, p)

def montgomery_to_weierstrass_point(P, CM, CW):
    """
    Maps a point on a montgomery curve CM onto one on the weierstrass curve CW
    """
    
    assert(CW == montgomery_to_weierstrass_curve(CM)), f"The Weierstrass curve {CW} is not mapped from the Montgomery curve {CM}"
    A, B, p = CM
    
    x, y = P
    t = (x * inverse(B, p) + A * inverse(3 * B, p)) % p
    v = (y * inverse(B, p)) % p
    
    Q = (t, v)
    assert(is_on_w(Q, CW))
    
    return Q

p = (1<<255) - 19
B = 1
A = 486662
curve = (A, B, p)
x = 4
P = lift(x, curve)
k = 0xfeed

Q = montgomery_binary(P, k, curve)

print(Q)

curve_w = montgomery_to_weierstrass_curve(curve)
print(curve_w)

T = montgomery_to_weierstrass_point(P, curve, curve_w)
print(T)

S = montgomery_to_weierstrass_point(Q, curve, curve_w)
print(S)

a, b, p = curve_w
CW = CurveFp(p, a, b)
T_ = Point(CW, *T)
S_ = Point(CW, *S)

print(S_ == k * T_)