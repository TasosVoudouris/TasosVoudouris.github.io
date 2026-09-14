# generates a random Sophie-Germaine prime (p=2*q+1 with q prime)
# we use these to make Fp^times as close to a cyclic group of prime order as possible
# this means a Pohlig-Hellman attack on Fp^* will have very little benefit
def random_sg_prime(bits):
    while true:
        p=random_prime(2^bits,2^(bits-1))
        if is_prime(2*p+1): break
    return p

def L(a,c,N):
    z = ceil(exp(c*log(N)^a*log(log(N))^(1-a)))
    if z%2: z+=1
    return ceil(z)

def trial_factor(x,B):
    f=[]
    lastp=0
    while x > 1:
        p=x.trial_division(B)
        if p > B: return []
        if p == lastp: f[-1][1] += 1
        else: f.append([p,1])
        x = x.divide_knowing_divisible_by(p)
        lastp = p
    return f
    
def dlog(a,b,p):
    B=ceil(2*L(1/2,1/2,p))
    print("smoothness bound is %d" % B)
    pi=[q for q in primes(B)]
    pimap=[0 for i in range(0,B)]
    i=0
    for q in primes(B):
        pimap[q] = i
        i += 1
    n=len(pi)
    print("factor base has %d elements, searching for relations..."%n)
    
    M=matrix(ZZ,n+2,n+2,sparse=true)
    t = cputime()
    bi = 1/b
    i = 0
    while i < M.nrows():
        e = randint(1,p-1)
        f=trial_factor(ZZ(a^e*bi),B)
        if f and f[-1][0] < B:
            for q in f:
                M[i,pimap[q[0]]]=q[1]
            M[i,n]=1; M[i,n+1]=e
            i += 1
    print("Found %d relations in %.2f s, attempting to solve system"%(i,cputime()-t))
    q = ZZ((p-1)/2)
    print(M)
    Mq=M.change_ring(GF(q)).echelon_form()
    M2=M.change_ring(GF(2)).echelon_form()
    print(Mq)
    print(M2)
    i = n; j = n
    while not Mq[i,n]: i-=1
    while not M2[j,n]: j-=1
    print(i,j,n)
    return ((q+1)*ZZ(Mq[i,n+1])+q*ZZ(M2[j,n+1]))%(2*q)

p=2*random_sg_prime(50)+1
print(p)
F=GF(p)
a=F.random_element()
while a.multiplicative_order() != p-1: a=F.random_element()
x=randint(1,p-1)
b=a^x
print("%d=%d^%d"%(b,a,x))
time y=dlog(a,b,p)
print("log_%d(%d) = %d"%(a,b,y))
assert x==y