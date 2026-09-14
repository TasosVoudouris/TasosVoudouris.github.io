##########encoding############
Q=41

def encode(x):
    return x % Q

def decode(x):
    return x if x <= Q/2 else x-Q

x = encode(501)
print("encoded: %d" % x)
print("decoded: %d" % decode(x))











