from Crypto.Util.number import inverse

# Integer square root function using Newton's method
def isqrt(n):
    x = n
    y = (x + 1) // 2
    while y < x:
        x = y
        y = (x + n // x) // 2
    return x

# Compute the multiplicative order of g modulo p
def order_of_elem(g: int, p: int):
    """
    Parameters:
    -----------
    g: int
        Generator element of a group G
    p: int 
        Prime modulus

    Returns:
    --------
    int
        Order of g such that g^n ≡ 1 mod p
    """
    N = 1
    temp = 1
    while True:
        temp = (temp * g) % p
        if temp == 1:
            break
        N += 1
    return N

# Example values
p = 17389              # Prime modulus
g = 2                  # Generator
h = 13896              # Target value such that g^x ≡ h mod p
N = order_of_elem(g, p)  # Compute the order of g modulo p
print(N)                 # Print the order
print(pow(g, N, p))      # Sanity check: g^N mod p should be 1

# Baby-Step Giant-Step algorithm to solve discrete log: find x such that g^x ≡ h mod p
def bsgs(g: int, h: int, p: int, N: int = None):
    """
    Parameters:
    -----------
    g: int
        Generator
    h: int
        h = g^x mod p
    p: int
        Prime modulus
    N: int, default = None
        Order of g. Computed if not provided

    Returns: 
    --------
    int
        x such that g^x ≡ h mod p, or None if no such x was found
    """
    # Compute the order of g if not provided
    if N is None:
        N = order_of_elem(g, p)
        
    n = isqrt(N) + 1  # Set baby-step/giant-step bound (⌈√N⌉)

    # Precompute and store all baby steps: g^j for j in [0, n]
    lookup_table = {pow(g, j, p): j for j in range(n + 1)}

    # Compute g^(-n) mod p for use in the giant steps
    c = inverse(pow(g, n, p), p)

    # Initialize value for giant steps
    temp = h
    for i in range(n + 1):
        # Compute h * (g^(-n))^i mod p
        temp = h * pow(c, i, p) % p

        # If collision with baby step found, return x = i*n + j
        if temp in lookup_table:
            return i * n + lookup_table[temp]

    # If no solution found, return None
    return None

# Run the algorithm to solve g^x ≡ h mod p
x = bsgs(g, h, p)
print(x)                     # The discrete log x
print(pow(g, x, p) == h)     # Verify the solution
