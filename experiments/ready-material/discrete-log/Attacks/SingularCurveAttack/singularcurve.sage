from collections import namedtuple

# Create a simple Point class to represent the affine points.
Point = namedtuple("Point", "x y")
Curve_custom = namedtuple("Curve", "a, b, c, p")
# The point at infinity (origin for the group law).
O = 'Origin'


# Check whether a point P lies on the singular cubic curve C
def check_point(P, C):
    if P == O:
        return True
    return (P.y^2 - (P.x^3 + C.a*P.x^2 + C.b*P.x + C.c)) % C.p == 0

# Return the elliptic inverse of a point
def point_inverse(P, C):
    if P == O:
        return P
    return Point(P.x, (-P.y) % C.p)

# Add two points on the curve using general formulas
def point_addition(P, Q, C):
    if P == O:
        return Q
    elif Q == O:
        return P
    elif Q == point_inverse(P, C):
        return O

    if P == Q:
        lam = (3*P.x^2 + 2*C.a*P.x + C.b) * inverse_mod(2*P.y, C.p) % C.p
    else:
        lam = (Q.y - P.y) * inverse_mod(Q.x - P.x, C.p) % C.p

    Rx = (lam^2 - C.a - P.x - Q.x) % C.p
    nu = (P.y - lam * P.x) % C.p
    Ry = (-lam * Rx - nu) % C.p

    return Point(Rx, Ry)

# Perform scalar multiplication via double-and-add
def double_and_add(n, P, C):
    R = O
    Q = P
    while n > 0:
        if n % 2 == 1:
            R = point_addition(R, Q, C)
        Q = point_addition(Q, Q, C)
        n = n // 2
    #assert check_point(R)
    return R



############ CUSPS ################ 

p = random_prime(2^256, lbound=2^255)
#Consider the equation with the triple root r 
r = 123
PF.<X> = PolynomialRing(GF(p))
f =  (X - r) ^ 3
print(f.roots())
#print(f)

c, b, a = int(f[0]), int(f[1]), int(f[2])
C = Curve_custom(a, b, c, p)
#print(check_point(Point(r+1,1), C))

########## Take a random point G and some message m => P

G = double_and_add(7, Point(r+1,1), C)
m = Integer(int.from_bytes(b'cryptoisfunifyouknowmathematics', 'big'))
P = double_and_add(m, G, C)
#print(check_point(G, C), check_point(P, C))

############## Define our isomorphism
def isomap(A, p):
    if (A.x, A.y) == (0,0):
        return 0
    else:
        return (A.x * inverse_mod(A.y, p)) % p

################ Shift our curve with the r to canonical cusp form: y^2 = x^3
f_shifted = f.subs(X = X + r)
print(f_shifted)
C_shifted = Curve_custom(f_shifted[2], f_shifted[1], f_shifted[0], p) # a b c are 0
#print(C_shifted)

# Translate points G and P by subtracting root r
G_shifted = Point((G.x - r) % p , G.y)
P_shifted = Point((P.x - r) % p, P.y)
#print(check_point(G_shifted, C_shifted), check_point(P_shifted, C_shifted))

############# Apply the x/y mapping on shifted points
P_map = isomap(P_shifted, p)
G_map = isomap(G_shifted, p)

# Compute original message integer via division in additive group
m_decr = (P_map * inverse_mod(G_map, p)) % p #additive inverse
#print(m_decr)
# Convert recovered integer back to plaintext
print(int(m_decr).to_bytes((m_decr.nbits() + 7)//8, 'big').decode('utf-8'))
