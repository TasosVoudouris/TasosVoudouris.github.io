import random
import math
import time
import hashlib
import struct

prime = 1035418103

while True:
    var_a = random.randint(1, prime)
    var_b = random.randint(1, prime)
    
    value = 4*math.pow(var_a, 3) + 27*math.pow(var_b, 2)
    
    if value != 0:
        break

# overwriting the values
prime = 1035418103
var_a = 45181635
var_b = 124806060

E = EllipticCurve(GF(prime), [1, 0, 0, var_a,var_b])

P = E.gen(0);
print('P: %s, n: %d' %(P, P.order()))

current_milli_time = lambda: int(round(time.time() * 1000))

def hash_function(point):
    bytes = struct.pack('f'*len(point), *point)
    return hashlib.md5(bytes).hexdigest()

def get_set(P, number_of_sets):
    hashdigest = hash_function(P)
    hash_as_int = int(hashdigest, 16)
    return 1 + (hash_as_int % number_of_sets)

def get_nextR(P, Q, R):
    if get_set(R, 3) == 1:
        nextR = Q + R
    elif get_set(R, 3) == 2:
        nextR = 2*R
    elif get_set(R, 3) == 3:
        nextR = P + R
    return nextR


def get_next_a_and_b(P, Q, a, b):
    n = P.order()
    R = a*P + b*Q
    
    if get_set(R, 3) == 1:
        next_a = a
        next_b = b + 1
    elif get_set(R, 3) == 2:
        next_a = 2*a % n
        next_b = 2*b % n
    elif get_set(R, 3) == 3:
        next_a = a + 1
        next_b = b
    return next_a, next_b


def pollards_rho_algorithm(P, Q):
    R = P
    a = 1
    b = 0
    
    # Initialize tortoise (R1) and hare (R2) for cycle detection
    R1 = get_nextR(P, Q, R)
    R2 = get_nextR(P, Q, R1)
    
    a1, b1 = get_next_a_and_b(P, Q, a, b)
    a2, b2 = get_next_a_and_b(P, Q, a1, b1)
    
    # Iterate until collision is found
    while True:
        R1 = get_nextR(P, Q, R1)  # Single step
        R2 = get_nextR(P, Q, get_nextR(P, Q, R2))  # Double step
        
        a1, b1 = get_next_a_and_b(P, Q, a1, b1)
        a, b = get_next_a_and_b(P, Q, a2, b2)
        a2, b2 = get_next_a_and_b(P, Q, a, b)
        
        if R1 == R2:
            break
    
    # Collision found: R1 = R2 => a1*P + b1*Q = a2*P + b2*Q
    # Solve (a2 - a1)P = (b1 - b2)Q => k ≡ (a2 - a1)/(b1 - b2) mod n
    diff_a = a2 - a1
    diff_b = b1 - b2

    return (diff_a / diff_b) % P.order()

k = random.randint(0, prime)
Q = k*P

print('k: %d, Q: %s' %(k,Q))
start_timestamp = current_milli_time()
x = pollards_rho_algorithm(P, Q)
end_timestamp = current_milli_time()

print('Time elapsed', end_timestamp - start_timestamp)
print('Solution: %s, Collision successful? %s' %(x, x*P == Q))