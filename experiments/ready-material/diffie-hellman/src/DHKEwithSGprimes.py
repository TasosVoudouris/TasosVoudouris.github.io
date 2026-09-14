import random
from random import SystemRandom #


def Miller_Rabin(p, base):
    '''
    Tests whether p is prime, using the given base.
    The result False implies that p is definitely not prime.
    The result True implies that p **might** be prime.
    It is not a perfect test!
    '''
    result = 1
    exponent = p-1
    modulus = p
    bitstring = bin(exponent)[2:] # Chop off the '0b' part of the binary expansion of exponent
    for bit in bitstring: # Iterates through the "letters" of the string.  Here the letters are '0' or '1'.
        sq_result = result*result % modulus  # We need to compute this in any case.
        if sq_result == 1:
            if (result != 1) and (result != exponent):  # Note that exponent is congruent to -1, mod p.
                return False  # a ROO violation occurred, so p is not prime
        if bit == '0':
            result = sq_result 
        if bit == '1':
            result = (sq_result * base) % modulus
    if result != 1:
        return False  # a FLT violation occurred, so p is not prime.
    
    return True  # If we made it this far, no violation occurred and p might be prime.

def is_prime(p, witnesses=50):  # witnesses is a parameter with a default value.
    '''
    Tests whether a positive integer p is prime.
    For p < 2^64, the test is deterministic, using known good witnesses.
    Good witnesses come from a table at Wikipedia's article on the Miller-Rabin test,
    based on research by Pomerance, Selfridge and Wagstaff, Jaeschke, Jiang and Deng.
    For larger p, a number (by default, 50) of witnesses are chosen at random.
    '''
    if (p%2 == 0): # Might as well take care of even numbers at the outset!
        if p == 2:
            return True
        else:
            return False 
    
    if p > 2**64:  # We use the probabilistic test for large p.
        trial = 0
        while trial < witnesses:
            trial = trial + 1
            witness = random.randint(2,p-2) # A good range for possible witnesses
            if Miller_Rabin(p,witness) == False:
                return False
        return True
    
    else:  # We use a determinisic test for p <= 2**64.
        verdict = Miller_Rabin(p,2)
        if p < 2047:
            return verdict # The witness 2 suffices.
        verdict = verdict and Miller_Rabin(p,3)
        if p < 1373653:
            return verdict # The witnesses 2 and 3 suffice.
        verdict = verdict and Miller_Rabin(p,5)
        if p < 25326001:
            return verdict # The witnesses 2,3,5 suffice.
        verdict = verdict and Miller_Rabin(p,7)
        if p < 3215031751:
            return verdict # The witnesses 2,3,5,7 suffice.
        verdict = verdict and Miller_Rabin(p,11)
        if p < 2152302898747:
            return verdict # The witnesses 2,3,5,7,11 suffice.
        verdict = verdict and Miller_Rabin(p,13)
        if p < 3474749660383:
            return verdict # The witnesses 2,3,5,7,11,13 suffice.
        verdict = verdict and Miller_Rabin(p,17)
        if p < 341550071728321:
            return verdict # The witnesses 2,3,5,7,11,17 suffice.
        verdict = verdict and Miller_Rabin(p,19) and Miller_Rabin(p,23)
        if p < 3825123056546413051:
            return verdict # The witnesses 2,3,5,7,11,17,19,23 suffice.
        verdict = verdict and Miller_Rabin(p,29) and Miller_Rabin(p,31) and Miller_Rabin(p,37)
        return verdict # The witnesses 2,3,5,7,11,17,19,23,29,31,37 suffice for testing up to 2^64. 
    
def is_SGprime(p):
    '''
    Tests whether p is a Sophie Germain prime
    '''
    if is_prime(p):  # A bit faster to check whether p is prime first.
        if is_prime(2*p + 1):  # and *then* check whether 2p+1 is prime.
            return True
    return False

def is_primroot_safe(b,p):
    '''
    Checks whether b is a primitive root modulo p,
    when p is a safe prime.  If p is not safe,
    the results will not be good!
    '''
    q = (p-1) // 2   # q is the Sophie Germain prime
    if b%p == 1:  # Is the multiplicative order 1?
        return False
    if (b*b)%p == 1:  # Is the multiplicative order 2?
        return False
    if pow(b,q,p) == 1:  # Is the multiplicative order q?
        return False
    return True  # If not, then b is a primitive root mod p.


r = SystemRandom().getrandbits(256)
print("The random integer is {}".format(r))
print("with binary expansion {}".format(bin(r)))  #  r is an integer constructed from 256 random bits.
print("with bit-length {}.".format(len(bin(r)) - 2))  # In case you want to check.  Remember '0b' is at the beginning.
def getrandSGprime(bitlength):
    '''
    Creates a random Sophie Germain prime p with about 
    bitlength bits.
    '''
    while True:
        p = SystemRandom().getrandbits(bitlength) # Choose a really random number.
        if is_SGprime(p):
            return p    

q = getrandSGprime(256) # A random ~256 bit Sophie Germain prime
p = 2*q + 1 # And its associated safe prime

print("p is ",p)  # Just to see what we're working with.
print("q is ",q)

def findprimroot_safe(p):
    '''
    Finds a primitive root, 
    modulo a safe prime p.
    '''
    b = 2  # Start trying with 2.
    while True:  # We just keep on looking.
        if is_primroot_safe(b,p):
            return b
        b = b + 1 # Try the next base.  Shouldn't take too long to find one!
g = findprimroot_safe(p)
print(g)

### Alice and Bob's private secrets
a = SystemRandom().getrandbits(256)  # Alice's secret number
b = SystemRandom().getrandbits(256)  # Bob's secret number

print("Only Alice should know that a = {}".format(a))
print("Only Bob should know that b = {}".format(b))

print("But everyone can know p = {} and g = {}".format(p,g))

A = pow(g,a,p)  # This would be computed on Alice's computer.
B = pow(g,b,p)  # This would be computed on Bob's computer.


print("Everyone knows A = {} and B = {}.".format(A,B))

print(pow(B,a,p))  # This is what Alice computes.
print(pow(A,b,p))  # This is what Bob computes.

#### Common secret

S = pow(B,a,p)  # Or we could have used pow(A,b,p)
print(S)

assert S == pow(B,a,p)
assert S == pow(A,b,p)

