p=29
q=23 
N=p*q
print("Modulus is for the two primes p,q:",N) # modulus
phi=(p-1)*(q-1)
print("The euler function phi is:",phi) # euler phi function
e=3
print("if gcd(e,616) is one then we can procceed. It is :", gcd(e,616)) # e=3 is ok, later we gonna see the problems for small e

# compute d
d=mod(1/e,phi)
print("d:",d) 

# verify e and d
print("It must be 1. It is:",mod(e*d,phi))

# compute ciphertext
m=108
print("message is:",m)
c=power_mod(108,3,667)
print("ciphertext is:",c) 

# decrypt ciphertext
power_mod(ZZ(c),ZZ(d),N) 
assert m == power_mod(ZZ(c),ZZ(d),N) 
print("We decrypted correctly")