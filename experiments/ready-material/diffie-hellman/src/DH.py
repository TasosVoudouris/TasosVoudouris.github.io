import random
from Crypto.Util.number import getPrime
from Crypto.Random.random import randint

################  A VERY NAIVE EXAMPLE FOLLOWING THE DHKE.md file ###################

#### Joseph
import random
p = 17
g = 3
a = random.randint(2, p-2) ; a
J = pow(g, a, p) ; J

#### Helen

b = random.randint(2, p-2) ; b
H = pow(g, b, p)

#### Exchange and Compute Shared Secret

s1 = pow(H, a, p)

s2 = pow(J, b, p)

assert (s1==s2)

############################ A BIGGER EXAMPLE ###########################

p=getPrime(128)
print(f"the prime p is : {p}")
#generaly 2 is the most known generator for many Z/pZ groups
g=2

def getKey():
    n = randint(2,p-1)
    return n , pow(g,n,p)



na,A= getKey()
##Alice's private key = na
print(f"Alice's Public Key A = {A}")
nb,B=getKey()
##Bob's private key = nb
print(f"Bob's Public Key B = {B}")
assert nb != na

print( pow(A,nb,p)==pow(B,na,p))
#the Shared secret
SS=pow(A,nb,p)
print(f"the shared secret SS = {SS}")