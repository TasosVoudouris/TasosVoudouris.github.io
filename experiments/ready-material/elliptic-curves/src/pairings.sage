################################# TORSION POINTS #########################

K = GF(13)
E = EllipticCurve(K, [1, 0])
n = 2
En_points = E(0).division_points(n) # E(0) is the point at infinity
print(En_points)

print([n * P == E(0) for P in En_points]) # check all points 

############################### POINT COUNTING/TRACE OF FROBENIUS #############
q = 101
E = EllipticCurve(GF(q), [1, -1])
print(E.cardinality()) # number of points on the curve
print(bool(E.trace_of_frobenius() < 2 * sqrt(q))) # check inequality
print(E.trace_of_frobenius(), q + 1 - E.cardinality() ) # Trace of frobenius

########################### WEIL PAIRING #################################

# Define a prime field F = GF(631) and an elliptic curve E over F
p = 631
F = GF(p)
E = EllipticCurve(F, [30, 34])  # Short Weierstrass form: y^2 = x^3 + 30x + 34

# Print the number of points on the elliptic curve
print(E.order())

# Define two points P and Q on the curve
P = E(36, 60)
Q = E(121, 387)

# Compute the order of P and Q
m = P.order()
print(P.order(), Q.order())

# Compute the Weil pairing e_m(P, Q), which should be an m-th root of unity
print(P.weil_pairing(Q, m), P.weil_pairing(Q, m)^m)  # Second value checks that result^m = 1

# Check that Weil pairing is alternating: e_m(P, P) = 1
print(P.weil_pairing(P, m))  # Should be 1 in multiplicative group of F

# Verify bilinearity of Weil pairing
P1 = E(36, 60)
Q1 = E(121, 387)
P2 = E(617, 5)
Q2 = E(121, 244)

# Confirm orders of the second set of points
print(P2.order(), Q2.order())

# Check bilinearity property: e_m(P1 + P2, Q1) = e_m(P1, Q1) * e_m(P2, Q1)
print((P1 + P2).weil_pairing(Q1, m) == P1.weil_pairing(Q1, m) * P2.weil_pairing(Q1, m))

# Similarly: e_m(P1, Q1 + Q2) = e_m(P1, Q1) * e_m(P1, Q2)
print(P1.weil_pairing(Q1 + Q2, m) == P1.weil_pairing(Q1, m) * P1.weil_pairing(Q2, m))

########################### TATE PAIRING #################################

# Define a new field GF(101) and elliptic curve E: y^2 = x^3 + 1 over it
p = 101
F = GF(p)
E = EllipticCurve(F, [0, 1])

# Get and print the order of the elliptic curve
E_order = E.order()
print(E_order)
print(factor(E_order))  # Factor the order to identify subgroup sizes

# Pick a nontrivial point P and compute its order m
P = 6 * E.an_element()
m = P.order()
print(m)

# Find embedding degree k such that m divides p^k - 1
k = GF(m)(p).multiplicative_order()
print(k)

# Alternative search for k (embedding degree) manually
k = 1
i = 1
while True:
    i += 1
    if (p^i - 1) % m == 0:
        k = i
        break
print(k)

# Compute the Tate pairing t_m(P, P) ∈ μ_m
print(P.tate_pairing(P, m, k))

# Choose another point Q and compute its order
Q = 17 * E.an_element()
print(Q.order())

# Compute Tate pairing t_m(P, Q)
print(P.tate_pairing(Q, m, k))
