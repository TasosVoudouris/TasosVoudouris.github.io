R.<x,y,A,B>=PolynomialRing(Rationals())

def reduce_poly_once(f):
    g = R(0)
    for t in f.monomials():
        if t.mod(y^2) == 0:
            g += f.monomial_coefficient(t)*R(t/y^2*(x^3+A*x+B))
        else:
            g += f.monomial_coefficient(t)*t
    return g

def reduce_poly(f):
    while f.degrees()[1] > 1: f = reduce_poly_once(f)
    return f

def reduce_point(P):
    return (reduce_poly(P[0]),reduce_poly(P[1]),reduce_poly(P[2]))

def dbl(P):
    x1= P[0]; y1=P[1]; z1=P[2]
    x3=x1^4-2*A*x1^2*z1^4-8*B*x1*z1^6+A^2*z1^8
    y3=x1^6+5*A*x1^4*z1^4+20*B*x1^3*z1^6-5*A^2*x1^2*z1^8-4*A*B*x1*z1^10-(A^3+8*B^2)*z1^12
    z3=2*y1*z1
    return reduce_point((x3,y3,z3))

def add(P,Q):
    if compare_point(P,Q): return dbl(P)
    x1=P[0]; y1=P[1]; z1=P[2]; x2=Q[0]; y2=Q[1]; z2=Q[2]
    x3 = A*(x1*z2^2+x2*z1^2)*z1^2*z2^2 + 2*B*z1^4*z2^4 + x1^2*x2*z2^2+x1*x2^2*z1^2-2*y1*y2*z1*z2
    y3 =(A*x2*z2+B*z2^3)*y2*z1^6 - (A*x1*z1+B*z1^3)*y1*z2^6+2*(x2^3*y1*z1^3 - x1^3*y2*z2^3) + 3*x1*x2*z1*z2*(x1*y2*z1 - x2*y1*z2)  + 3*y1*y2*(y1*z2^3 - y2*z1^3)
    z3 = x1*z2^2-x2*z1^2
    return reduce_point((x3,y3,z3))

def compare_point(P,Q):
    return (P[0]*Q[2]^2 == Q[0]*P[2]^2 and P[1]*Q[2]^3 == Q[1]*P[2]^3)


# compute the first 7 division polynomials using the group law
# NB: to avoid introducing extra factors compute P[2m+1] as P[m]+P[m+1] and P[2m]=P[m]+P[m]
# It will also work with arbitrary additions, but this may require removing common factors from the coordinates
# A more complicated version of reduce_point that does this is provided below.
P = [(R(0),R(1),R(0))]                   # point at infinity
P.append((R(x),R(y),R(1)))               # generic point P
P.append(dbl(P[1]))        # 2P = P + P
P.append(add(P[2],P[1]))   # 3P = 2P + P
P.append(dbl(P[2]))        # 4P = 2P + 2P
P.append(add(P[2],P[3]))   # 5P = 2P + 3P
P.append(dbl(P[3]))        # 6P = 3P + 3P
P.append(add(P[3],P[4]))   # 7P = 3P + 4P

for n in range(1,8): print("%d, %s, %s, %s"%(n,P[n][0], P[n][1], P[n][2]))


# compute first 7 division polynomials using recurrence relations
M=8

psi=[R(0) for m in range(0,M+2)]
for m in range(0,5):
    psi[m]=P[m][2]
psi[3]=-psi[3]    # fix sign of psi_3 to match definition

# note that we need psi[m+2] to compute omega[m]
for n in range(5,M+2):
    m = n//2
    if n==2*m:
        psi[2*m]  =reduce_poly(R(psi[m]*(psi[m+2]*psi[m-1]^2-psi[m-2]*psi[m+1]^2)/(2*y)))
    else:
        psi[2*m+1]=reduce_poly(psi[m+2]*psi[m]^3-psi[m-1]*psi[m+1]^3)

phi=[R(0) for m in range(0,M)]
for m in range(1,M): phi[m] = reduce_poly(x*psi[m]^2-psi[m+1]*psi[m-1])

omega=[R(0) for m in range(0,M)]
omega[0]=1
omega[1]=y
for m in range(2,M): omega[m] = reduce_poly(R((psi[m+2]*psi[m-1]^2-psi[m-2]*psi[m+1]^2)/(4*y)))

# verify that we get the same result using the recurrences as when we used the group law
for m in range(1,M):
    print("%d: %s"%(m,compare_point(P[m],(phi[m],omega[m],psi[m]))))


# this is a more thorough point reduction function that removes common factors
def reduce_point(P):
    x3 = reduce_poly(P[0])
    y3 = reduce_poly(P[1])
    z3 = reduce_poly(P[2])
    z32 = reduce_poly(z3^2)
    z33 = reduce_poly(z3^3)
    h = R((y3*numerator(x3/z32)) / (x3*numerator(y3/z33)))
    x3 = R(x3/h^2); y3 = R(y3/h^3); z3 = R(z3/h)
    if z3.mod(y) == 0 and x3.mod(x^3+A*x+B) == 0 and y3.mod((x^3+A*x+B)^2) == 0:
        z3 = R(z3/y); x3 = R(x3/(x^3+A*x+B)); y3 = R(y*y3/(x^3+A*x+B)^2)
    if z3.mod(x^3+A*x+B) == 0 and x3.mod(x^3+A*x+B) == 0 and y3.mod((x^3+A*x+B)*y) == 0:
        z3 = R(y*z3/(x^3+A*x+B)); x3 = R(x3/(x^3+A*x+B)); y3 = R(y3/(y*(x^3+A*x+B)))
    xc = gcd([int(c) for c in x3.coefficients()])
    yc = gcd([int(c) for c in y3.coefficients()])
    zc = gcd([int(c) for c in z3.coefficients()])
    if zc%2 == 0 and xc%4 == 0 and yc%8 == 0:
        z3 = R(z3/2); x3 = R(x3/4); y3 = R(y3/8);
    xc = gcd([int(c) for c in x3.coefficients()])
    yc = gcd([int(c) for c in y3.coefficients()])
    zc = gcd([int(c) for c in z3.coefficients()])
    if zc%2 == 0 and xc%4 == 0 and yc%8 == 0:
        z3 = R(z3/2); x3 = R(x3/4); y3 = R(y3/8);
    return (x3,y3,z3)

print(P[7][1])