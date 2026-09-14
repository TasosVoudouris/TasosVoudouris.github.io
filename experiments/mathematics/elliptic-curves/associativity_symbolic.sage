RR.<Px,Py,Qx,Qy,Rx,Ry,A,B> = PolynomialRing(ZZ,8)
# We represent projective points on E uniquely, as affine points (x,y,1) or the point O=(0,1,0) at infinity
P=(Px,Py,1); Q=(Qx,Qy,1); R=(Rx,Ry,1); O=(0,1,0);
I=RR.ideal(Py^2-Px^3-A*Px-B, Qy^2-Qx^3-A*Qx-B, Ry^2-Rx^3-A*Rx-B)
SS=RR.quotient(I)

def add(P,Q):
    """ general addition algorithm for an elliptic curve in short Weierstrass form"""
    if P == O: return Q
    if Q == O: return P
    assert P[2] == 1 and Q[2] == 1  # we are using affine formulas, so make sure points are in affine form
    x1=P[0]; y1=P[1]; x2=Q[0]; y2=Q[1];
    if x1 != x2:
        m = (y2-y1)/(x2-x1)         # usual case: P and Q are distinct and not opposites
    else:
        if y1 == -y2: return O      # P = -Q (includes case where P=Q is 2-torsion)
        m = (3*x1^2+A) / (2*y1)     # P = Q so we are doubling
    x3 = m^2-x1-x2
    y3 = m*(x1-x3)-y1
    return (x3,y3,1)

def negate(P):
    if P == O: return O
    return (P[0],-P[1],P[2])

def reduced_fractions_equal(p,q):
    """
    Verifies the inputs p and q are well-defined elements of the fraction field of SS in any char != 2,
    then tests whether they are equal as elements of the fraction field of SS.

    We exclude characteristic 2 because we are using formulas for curves in short Weierstrass form,
    but if we generalized the formulas to curves in general Weierstrass form we could also handle char 2.
    This is also necessary to handle all curves in char 3 (the formulas here are valid in char 3 but not
    every elliptic curve can be put in the form y^2 = x^3 + Ax + B in characteristic 3).

    Note that while we are working with polynomials over ZZ we have a will defined reduction map to polynomials
    over any ring.  We can verify that a polynomial will be nonzero in any field of characteristic p != 2
    by verifying that the GCD of the coefficients is 1 or a power of 2.
    """
    # The call to prime_divisors below will fail on 0, which is good
    assert gcd(SS(p.denominator()).lift().coefficients()).prime_divisors() in [[],[2]]
    assert gcd(SS(q.denominator()).lift().coefficients()).prime_divisors() in [[],[2]]
    return SS(p.numerator()*q.denominator()-p.denominator()*q.numerator()) == 0

def on_curve(P):
    return reduced_fractions_equal(P[1]^2*P[2],P[0]^3+A*P[0]*P[2]^2+B*P[2]^3)

def equal(P,Q):
    return reduced_fractions_equal(P[0]*Q[2],Q[0]*P[2]) and reduced_fractions_equal(P[1]*Q[2],Q[1]*P[2])

def passert(predicate):
    if eval(predicate):
        print("Confirmed assertion %s" % predicate)
    else:
        print("Failed to confirm assertion %s" % predicate)
        # raise ValueError("Assertion %s FAILED" % predicate)

passert("on_curve(O) and on_curve(negate(P)) and on_curve(add(P,Q)) and on_curve(add(P,P)) and on_curve(add(P,negate(P)))")
passert("add(P,O) == P and add(O,P) == P")
passert("add(P,negate(P)) == O")
passert("add(P,Q) == add(Q,P)")


##### GENERAL CASE? ####

####  passert("add(add(P,Q),R) == add(P,add(Q,R))") ### THIS SHOULD OUTPUT FAIL BECAUSE YOU NEED TO USE THE CURVE EQUATION AND USE THE EQUAL FUNCTION WHICH REDUCES INTO THE QUOTIENT ring

passert("equal(add(add(P,Q),R),add(P,add(Q,R)))") ### THIS SHOULD WORK FINE


passert("equal(add(add(P,P),Q),add(P,add(P,Q))) and equal(add(add(P,Q),P),add(P,add(Q,P))) and equal(add(add(Q,P),P),add(Q,add(P,P)))") ####### 2-points

S = negate(P);
passert("equal(add(add(P,S),Q),add(P,add(S,Q))) and equal(add(add(P,Q),S),add(P,add(Q,S))) and equal(add(add(Q,P),S),add(Q,add(P,S)))") ### 2- POINTS THAT ARE OPPOSITES 

passert("equal(add(add(P,P),P),add(P,add(P,P)))") ### THREE POINTS

#### IT WORKS FOR EVERYTHING EVEN FOR "STRANGE THINGS" ######

passert("equal(add(add(P,Q),add(P,Q)),add(P,add(Q,add(P,Q)))) and equal(add(add(P,Q),add(P,negate(Q))),add(P,add(Q,add(P,negate(Q)))))")
passert("equal(add(add(P,Q),negate(add(P,Q))),add(P,add(Q,negate(add(P,Q)))))")
passert("equal(add(add(P,Q),add(P,P)),add(P,add(Q,add(P,P)))) and equal(add(add(P,Q),negate(add(P,P))),add(P,add(Q,negate(add(P,P)))))")


#### WHAT WE ACTUALLY TESTED IF ITS EQUAL? ####

print(add(add(P,Q),R), "\n\n    versus   \n\n", add(P,add(Q,R)))