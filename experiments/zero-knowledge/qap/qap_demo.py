"""Convert the CryptoCave 3-constraint R1CS example into a tiny QAP.

The code interpolates one polynomial per witness column, combines those
polynomials with the witness, and verifies that A(X)B(X)-C(X) is divisible by
t(X)=(X-1)(X-2)(X-3). Pure Python, tiny prime field, educational only.
"""
P = 97

A_ROWS = [
    [0, 1, 0, 0, 0, 0],
    [0, 0, 1, 0, 0, 0],
    [0, -1, 0, 0, 0, 0],
]
B_ROWS = [
    [0, 1, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 0],
    [0, 0, 0, 0, 1, 0],
]
C_ROWS = [
    [0, 0, 1, 0, 0, 0],
    [0, 0, 0, 1, 0, 0],
    [-4, 0, -4, -1, 0, 1],
]


def trim(a):
    a=[x%P for x in a]
    while len(a)>1 and a[-1]==0: a.pop()
    return a

def add(a,b):
    n=max(len(a),len(b)); out=[0]*n
    for i in range(n): out[i]=((a[i] if i<len(a) else 0)+(b[i] if i<len(b) else 0))%P
    return trim(out)
def sub(a,b): return add(a,[(-x)%P for x in b])
def mul(a,b):
    out=[0]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b): out[i+j]=(out[i+j]+x*y)%P
    return trim(out)
def scale(a,c): return trim([(c*x)%P for x in a])
def evalp(a,x):
    r=0
    for c in reversed(a): r=(r*x+c)%P
    return r

def divmodp(num,den):
    num=trim(num[:]); den=trim(den[:])
    if den==[0]: raise ZeroDivisionError
    q=[0]*max(1,(len(num)-len(den)+1))
    inv=pow(den[-1],-1,P)
    while len(num)>=len(den) and num!=[0]:
        k=len(num)-len(den); c=num[-1]*inv%P; q[k]=c
        num=sub(num,[0]*k+scale(den,c))
    return trim(q),trim(num)

def lagrange(xs,ys):
    out=[0]
    for i,(xi,yi) in enumerate(zip(xs,ys)):
        basis=[1]; denom=1
        for j,xj in enumerate(xs):
            if i==j: continue
            basis=mul(basis,[(-xj)%P,1]); denom=denom*(xi-xj)%P
        out=add(out,scale(basis,yi*pow(denom,-1,P)%P))
    return trim(out)

def columns(rows): return list(map(list,zip(*rows)))

def combine(polys,w):
    out=[0]
    for poly,wi in zip(polys,w): out=add(out,scale(poly,wi))
    return out


def self_test():
    xs=[1,2,3]
    A=[lagrange(xs,col) for col in columns(A_ROWS)]
    B=[lagrange(xs,col) for col in columns(B_ROWS)]
    C=[lagrange(xs,col) for col in columns(C_ROWS)]
    x,z,y=7,2,529
    w=[1,x,x*x,x*x*x,z,y]
    w=[v%P for v in w]
    Ap,Bp,Cp=combine(A,w),combine(B,w),combine(C,w)
    p=sub(mul(Ap,Bp),Cp)
    t=[1]
    for xi in xs: t=mul(t,[(-xi)%P,1])
    h,r=divmodp(p,t)
    assert r==[0]
    assert p==mul(h,t)
    for xi in xs: assert evalp(p,xi)==0
    print("R1CS -> QAP interpolation: PASS")
    print("QAP divisibility check: PASS")


if __name__ == "__main__": self_test()
