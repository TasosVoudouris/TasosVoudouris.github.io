import random

SMALL_PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311, 313, 317, 331, 337, 347, 349, 353, 359, 367, 373, 379, 383, 389, 397, 401, 409, 419, 421, 431, 433, 439, 443, 449, 457, 461, 463, 467, 479, 487, 491, 499, 503, 509, 521, 523, 541, 547, 557, 563, 569, 571, 577, 587, 593, 599, 601, 607, 613, 617, 619, 631, 641, 643, 647, 653, 659, 661, 673, 677, 683, 691, 701, 709, 719, 727, 733, 739, 743, 751, 757, 761, 769, 773, 787, 797, 809, 811, 821, 823, 827, 829, 839, 853, 857, 859, 863, 877, 881, 883, 887, 907, 911, 919, 929, 937, 941, 947, 953, 967, 971, 977, 983, 991, 997]

def rewrite(num):
    s = num - 1
    t = 0
    while s % 2 == 0:
        s = s // 2
        t += 1
    return s, t

def rabin_miller(num, iterations=10):
    s, t = rewrite(num)
    for _ in range(iterations):
        a = random.randrange(2, num - 1)
        v = pow(a, s, num)
        if v != 1:
            i = 0
            while v != (num - 1):
                if i == t - 1:
                    return False
                else:
                    i = i + 1
                    v = pow(v, 2, num)
    return True

def is_prime(num):
    if (num < 2): return False
    for prime in SMALL_PRIMES:
        if num == prime: return True
        if num % prime == 0: return False
    return rabin_miller(num)


#################### Parameter generation ########################

def is_power_of(x, base):
    p = 1
    while p < x:
        p = p * base
    return p == x

################################# Sampling primes through a randomized primality test ########################
def sample_prime(bitsize):
    lower = 1 << (bitsize-1)
    upper = 1 << (bitsize)
    while True:
        candidate = random.randrange(lower, upper)
        if is_prime(candidate):
            return candidate

assert(is_prime(sample_prime(5)))
assert(is_prime(sample_prime(128)))


def remove_factor(x, factor):
    while x % factor == 0:
        x //= factor
    return x
    

def prime_factor(x):
    factors = []
    for prime in SMALL_PRIMES:
        if prime > x: break
        if x % prime == 0:
            factors.append(prime)
            x = remove_factor(x, prime)
    assert(x == 1) # fail if we were trying to factor a too large number
    return factors

################ find a prime q with the desired structure (i.e. of a certain minimum size and whose order q-1 has a given divisor) #############
def find_prime(min_bitsize, order_divisor):
    while True:
        k1 = sample_prime(min_bitsize)
        for k2 in range(128):
            q = k1 * k2 * order_divisor + 1
            if is_prime(q):
                order_prime_factors  = [k1]
                order_prime_factors += prime_factor(k2)
                order_prime_factors += prime_factor(order_divisor)
                return q, order_prime_factors

########################find a generator #############################
def find_generator(q, order_prime_factors):
    order = q - 1
    for candidate in range(2, q):
        for factor in order_prime_factors:
            exponent = order // factor
            if pow(candidate, exponent, q) == 1:
                break
        else:
            return candidate


############################# find a prime field with the above generator #######################
def find_prime_field(min_bitsize, order_divisor):
    q, order_prime_factors = find_prime(min_bitsize, order_divisor)
    g = find_generator(q, order_prime_factors)
    return q, g

assert(find_prime_field(2, 8*9) == (433, 5))


######  takes a desired minimum field size in bits, as well as the number of secrets k we which to packed together, the privacy threshold t we want, and the number n of shares to generate. ############
def generate_parameters(min_bitsize, order2, order3):
    assert(is_power_of(order2, 2))
    assert(is_power_of(order3, 3))
    
    order_divisor = order2 * order3
    q, g = find_prime_field(min_bitsize, order_divisor)
    assert(is_prime(q))
    
    order = q - 1
    assert(order % order2 == 0)
    assert(order % order3 == 0)
    omega2 = pow(g, order // order2, q)
    omega3 = pow(g, order // order3, q)
    
    return q, omega2, omega3
    
assert(generate_parameters(2, 8, 9) == (433, 354, 150))


######################### Either generate new parameters ... ####################
#ORDER2 = 512
#ORDER3 = 729
#Q, OMEGA2, OMEGA3 = generate_parameters(80, ORDER2, ORDER3)

#print("Prime is %d" % Q)
#print("%d-th principal root of unity is %d" % (ORDER2, OMEGA2))
#print("%d-th principal root of unity is %d" % (ORDER3, OMEGA3))


############ .. or use a fixed choice ... ######################

ORDER2 = 16
ORDER3 = 27


Q = 433
OMEGA2 = 354
OMEGA3 = 150


Q, OMEGA2, OMEGA3 = generate_parameters(80, ORDER2, ORDER3)

print("Prime is %d" % Q)
print("%d-th principal root of unity is %d" % (ORDER2, OMEGA2))
print("%d-th principal root of unity is %d" % (ORDER3, OMEGA3))

################# this will work either way #########################
assert(is_prime(Q))

assert(is_power_of(ORDER2, 2))
assert(is_power_of(ORDER3, 3))

ORDER = Q - 1
assert(ORDER % ORDER2 == 0)
assert(ORDER % ORDER3 == 0)

assert(pow(OMEGA2, ORDER2, Q) == 1) # root of unity
assert(1 not in ( pow(OMEGA2, e, Q) for e in range(1, ORDER2) )) # principal 

assert(pow(OMEGA3, ORDER3, Q) == 1) # root of unity
assert(1 not in ( pow(OMEGA3, e, Q) for e in range(1, ORDER3) )) # principal



################################# helper funnctions ####################################

def egcd_binary(a, b):
    u, v, s, t, r = 1, 0, 0, 1, 0
    while (a % 2 == 0) and (b % 2 == 0):
        a, b, r = a//2, b//2, r+1
    alpha, beta = a, b
    while (a % 2 == 0):
        a = a//2
        if (u % 2 == 0) and (v % 2 == 0):
            u, v = u//2, v//2
        else:
            u, v = (u + beta)//2, (v - alpha)//2
    while a != b:
        if (b % 2 == 0):
            b = b//2
            if (s % 2 == 0) and (t % 2 == 0):
                s, t = s//2, t//2
            else:
                s, t = (s + beta)//2, (t - alpha)//2
        elif b < a:
            a, b, u, v, s, t = b, a, s, t, u, v
        else:
            b, s, t = b - a, s - u, t - v
    return (2 ** r) * a, s, t


def inverse(a):
    _, b, _ = egcd_binary(a, Q)
    return b


for a in range(1, min(Q, 1000000)):
    assert(a * inverse(a) % Q == 1)


def eval_poly_at(coefs, point):
    return sum( coef * pow(point, degree, Q) % Q for degree, coef in enumerate(coefs) ) % Q

if Q > 17:
    assert(eval_poly_at([1,2,3], 0) == 1 % Q)
    assert(eval_poly_at([1,2,3], 1) == 6 % Q)
    assert(eval_poly_at([1,2,3], 2) == 17 % Q)    


######################################### FFT UNOPTIMISED ###################################
# len(A_coeffs) must be a power of 2
def fft2_forward(A_coeffs, omega=OMEGA2):
    if len(A_coeffs) == 1:
        return A_coeffs

    # split A into B and C such that A(x) = B(x^2) + x C(x^2)
    B_coeffs = A_coeffs[0::2]
    C_coeffs = A_coeffs[1::2]
    
    # apply recursively
    omega_squared = pow(omega, 2, Q)
    B_values = fft2_forward(B_coeffs, omega_squared)
    C_values = fft2_forward(C_coeffs, omega_squared)
        
    # combine subresults
    A_values = [0] * len(A_coeffs)
    L_half = len(A_coeffs) // 2
    for i in range(0, L_half):
        
        j = i
        x = pow(omega, j, Q)
        A_values[j] = (B_values[i] + x * C_values[i]) % Q
        
        j = i + L_half
        x = pow(omega, j, Q)
        A_values[j] = (B_values[i] + x * C_values[i]) % Q
        
    return A_values

def fft2_backward(A_values):
    L_inv = inverse(len(A_values))
    A_coeffs = [ (a * L_inv) % Q for a in fft2_forward(A_values, inverse(OMEGA2)) ]
    return A_coeffs


coefs = [ x for x in range(ORDER2) ]
assert(len(coefs) == ORDER2)

values = fft2_forward(coefs)
assert(len(values) == ORDER2)
assert(values == [ eval_poly_at(coefs, pow(OMEGA2, degree, Q)) for degree in range(ORDER2) ])
print(values)

coefs_recovered = fft2_backward(values)
assert(coefs == coefs_recovered)

print(coefs_recovered)



# len(A_coeffs) must be a power of 3
def fft3_forward(A_coeffs, omega=OMEGA3):
    if len(A_coeffs) == 1:
        return A_coeffs

    # split A(x) into B(x), C(x), and D(x) such that A(x) = B(x^3) + x C(x^3) + x^2 D(x^3)
    B_coeffs = A_coeffs[0::3]
    C_coeffs = A_coeffs[1::3]
    D_coeffs = A_coeffs[2::3]
    
    # apply recursively
    omega_cubed = pow(omega, 3, Q)
    B_values = fft3_forward(B_coeffs, omega_cubed)
    C_values = fft3_forward(C_coeffs, omega_cubed)
    D_values = fft3_forward(D_coeffs, omega_cubed)
        
    # combine subresults
    A_values = [0] * len(A_coeffs)
    L_third = len(A_coeffs) // 3
    for i in range(L_third):
        
        j = i
        x = pow(omega, j, Q)
        xx = (x * x) % Q
        A_values[j] = (B_values[i] + x * C_values[i] + xx * D_values[i]) % Q
        
        j = i + L_third
        x = pow(omega, j, Q)
        xx = (x * x) % Q
        A_values[j] = (B_values[i] + x * C_values[i] + xx * D_values[i]) % Q
        
        j = i + L_third + L_third
        x = pow(omega, j, Q)
        xx = (x * x) % Q
        A_values[j] = (B_values[i] + x * C_values[i] + xx * D_values[i]) % Q

    return A_values

def fft3_backward(A_values):
    L_inv = inverse(len(A_values))
    A_coeffs = [ (a * L_inv) % Q for a in fft3_forward(A_values, inverse(OMEGA3)) ]
    return A_coeffs


coefs = [ x for x in range(ORDER3) ]
assert(len(coefs) == ORDER3)

values = fft3_forward(coefs)
assert(len(values) == ORDER3)
assert(values == [ eval_poly_at(coefs, pow(OMEGA3, degree, Q)) for degree in range(ORDER3) ])

coefs_recovered = fft3_backward(values)
assert(coefs == coefs_recovered)



################################### FFT OPTIMIZED ###########################################

# len(aX) must be a power of 2
def fft2_forward(aX, omega=OMEGA2):
    if len(aX) == 1:
        return aX

    # split A(x) into B(x) and C(x) -- A(x) = B(x^2) + x C(x^2)
    bX = aX[0::2]
    cX = aX[1::2]
    
    # apply recursively
    omega_squared = pow(omega, 2, Q)
    B = fft2_forward(bX, omega_squared)
    C = fft2_forward(cX, omega_squared)
        
    # combine subresults
    A = [0] * len(aX)
    Nhalf = len(aX) >> 1
    point = 1
    for i in range(0, Nhalf):
        
        x = point
        A[i]         = (B[i] + x * C[i]) % Q
        A[i + Nhalf] = (B[i] - x * C[i]) % Q

        point = (point * omega) % Q
        
    return A

def fft2_backward(A):
    N_inv = inverse(len(A))
    return [ (a * N_inv) % Q for a in fft2_forward(A, inverse(OMEGA2)) ]


coefs = [ x for x in range(ORDER2) ]
assert(len(coefs) == ORDER2)

values = fft2_forward(coefs)
assert(len(values) == ORDER2)
assert(values == [ eval_poly_at(coefs, pow(OMEGA2, degree, Q)) for degree in range(ORDER2) ])

coefs_recovered = fft2_backward(values)
assert(coefs == coefs_recovered)


# len(aX) must be a power of 3
def fft3_forward(aX, omega=OMEGA3):
    if len(aX) == 1:
        return aX

    # split A(x) into B(x), C(x), and D(x): A(x) = B(x^3) + x C(x^3) + x^2 D(x^3)
    bX = aX[0::3]
    cX = aX[1::3]
    dX = aX[2::3]
    
    # apply recursively
    omega_cubed = pow(omega, 3, Q)
    B = fft3_forward(bX, omega_cubed)
    C = fft3_forward(cX, omega_cubed)
    D = fft3_forward(dX, omega_cubed)
        
    # combine subresults
    A = [0] * len(aX)
    Nthird = len(aX) // 3
    omega_Nthird = pow(omega, Nthird, Q)
    point = 1
    for i in range(Nthird):
        
        x = point
        xx = (x * x) % Q
        A[i                  ] = (B[i] + x * C[i] + xx * D[i]) % Q
        
        x = x * omega_Nthird % Q
        xx = (x * x) % Q
        A[i + Nthird         ] = (B[i] + x * C[i] + xx * D[i]) % Q
        
        x = x * omega_Nthird % Q
        xx = (x * x) % Q
        A[i + Nthird + Nthird] = (B[i] + x * C[i] + xx * D[i]) % Q

        point = (point * omega) % Q
        
    return A

def fft3_backward(A):
    N_inv = inverse(len(A))
    return [ (a * N_inv) % Q for a in fft3_forward(A, inverse(OMEGA3)) ]


coefs = [ x for x in range(ORDER3) ]
assert(len(coefs) == ORDER3)

values = fft3_forward(coefs)
assert(len(values) == ORDER3)
assert(values == [ eval_poly_at(coefs, pow(OMEGA3, degree, Q)) for degree in range(ORDER3) ])

coefs_recovered = fft3_backward(values)
assert(coefs == coefs_recovered)




##################################### PACKED SECRET SHARING ##################################

# N = ORDER3 - 1, which is the number of shares to be generated.
N = ORDER3 - 1

# T = N // 2, which is the privacy threshold (maximum number of shares you can lose and still reconstruct).
T = N // 2

# K is the number of secrets to be packed, derived from the size of ORDER2, adjusted by T.
K = ORDER2 - T - 1

# These assertions ensure that the sizes of ORDER2 and ORDER3 match the relations between N, T, and K.
assert(ORDER2 == T + K + 1)
assert(ORDER3 == N + 1)

# POINTS_SECRETS are the points where the secrets will be evaluated, based on OMEGA2 and Q.
# This ensures that the points for secrets are distinct and can be evaluated separately.
POINTS_SECRETS = set( pow(OMEGA2, e, Q) for e in range(1, ORDER2) )  # Secrets' evaluation points, incl randomness

# POINTS_SHARES are the points where the shares will be evaluated, based on OMEGA3 and Q.
POINTS_SHARES = set( pow(OMEGA3, e, Q) for e in range(1, ORDER3) )  # Shares' evaluation points

# Ensures that there is no intersection between POINTS_SECRETS and POINTS_SHARES.
assert(POINTS_SECRETS.intersection(POINTS_SHARES) == set([]))

# Debugging information: print the sorted points for secrets and shares.
print("Points used for secrets: %s" % sorted(POINTS_SECRETS))
print("Points used for shares:  %s" % sorted(POINTS_SHARES))


# Function to share the secret using FFT
def share(secrets):
    # Ensure that the length of the secrets matches K (the number of packed secrets).
    assert(len(secrets) == K)

    # Construct the small_values list, including the secrets and randomness for privacy.
    small_values = [0] + secrets + [random.randrange(Q) for _ in range(T)]

    # Perform the backward FFT on the small_values to get the coefficients for the polynomial.
    small_coeffs = fft2_backward(small_values)

    # Extend the small coefficients to match the size required by ORDER3 by padding with zeroes.
    large_coeffs = small_coeffs + [0] * (ORDER3 - ORDER2)

    # Perform the forward FFT on the large_coeffs to generate the share values.
    large_values = fft3_forward(large_coeffs)

    # Extract the shares by excluding the zero at the start (index 0) in large_values.
    shares = large_values[1:]

    # Validation to ensure that sizes match expectations for ORDER2 and ORDER3.
    assert(len(small_values) == ORDER2)
    assert(len(large_coeffs) == ORDER3)
    assert(len(shares) == N)

    return shares


# Function to reconstruct the secrets from the shares
def reconstruct(shares):
    # Ensure that the length of the shares is N.
    assert(len(shares) == N)

    # Add a zero at the start to match the format of large_values.
    large_values = [0] + shares

    # Perform the backward FFT on large_values to get the large_coeffs.
    large_coeffs = fft3_backward(large_values)

    # Extract the small coefficients, corresponding to the original polynomial.
    small_coeffs = large_coeffs[:ORDER2]

    # Perform the forward FFT on small_coeffs to get the small_values (which include the secrets).
    small_values = fft2_forward(small_coeffs)

    # Extract the secrets from the small_values (ignoring the first value, which was zero).
    secrets = small_values[1:K+1]

    # Validation to ensure that sizes match expectations.
    assert(len(large_values) == ORDER3)
    assert(large_coeffs[ORDER2:] == [0] * (ORDER3 - ORDER2))  # Ensure the padding is all zeros
    assert(len(small_coeffs) == ORDER2)
    assert(len(secrets) == K)

    return secrets


# Example use of the sharing and reconstruction functions:
# Create a list of secrets (from 1 to K).
secrets = [s for s in range(1, K + 1)]

# Generate shares for the given secrets.
shares = share(secrets)

# Reconstruct the secrets from the shares.
recovered_secrets = reconstruct(shares)

# Ensure that the reconstructed secrets match the original ones.
assert(recovered_secrets == secrets)
