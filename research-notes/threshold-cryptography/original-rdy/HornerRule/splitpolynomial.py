def horner_evaluate(coeffs, point):
    result = 0
    for coef in reversed(coeffs):
        result = (coef + point * result) % Q
    return result
Q = 433
OMEGA4 = 179

w = [ pow(OMEGA4, e, Q) for e in range(4) ]

print(w)
[1, 179, 432, 254]
A_coeffs = [ 1, 2, 3, 4 ]
A = lambda x: horner_evaluate(A_coeffs, x)

assert([ A(wi) for wi in w ]
    == [ 10, 73, 431, 356 ])
# split A into B and C
B_coeffs = A_coeffs[0::2] # == [ 1,    3,   ]
C_coeffs = A_coeffs[1::2] # == [    2,    4 ]

v = [ wi * wi % Q for wi in w ]

# compute values for B and C at v points
B = lambda x: horner_evaluate(B_coeffs, x)
C = lambda x: horner_evaluate(C_coeffs, x)
B_values = [ B(vi) for vi in v ]
C_values = [ C(vi) for vi in v ]
assert( B_values == [ B(vi) for vi in v ] )
assert( C_values == [ C(vi) for vi in v ] )

# combine results into values for A at w points
A_values = [ ( B_values[i] + w[i] * C_values[i] ) % Q for i,_ in enumerate(w) ]

assert( A_values == [ A(wi) for wi in w ] )


OMEGA2 = OMEGA4 * OMEGA4 % Q

w_squared = [ pow(OMEGA2, e, Q) for e in range(4) ]
print(w_squared)

v = [ pow(OMEGA2, e, Q) for e in range(2) ]
print(v)
#[1, 432, 1, 432]
#[1, 432]

print([ pow(OMEGA4, e, Q) for e in range(8) ])
print([ pow(OMEGA2, e, Q) for e in range(8) ])
#[1, 179, 432, 254, 1, 179, 432, 254]
#[1, 432, 1, 432, 1, 432, 1, 432]