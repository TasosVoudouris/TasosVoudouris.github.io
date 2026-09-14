import random

def bsgs_ecdlp(P, Q, E):
    if Q == E((0, 1, 0)):  # Point at infinity (zero element)
        return P.order()
    if Q == P:  # If Q is P, then the discrete log is 1
        return 1
    m = ceil(sqrt(P.order()))  # Compute the step size (square root of group order)
    
    # Baby-step phase: Precompute small multiples of P
    lookup_table = {j * P: j for j in range(m)}
    
    # Giant-step phase: Compute large jumps to match a baby-step
    for i in range(m):
        temp = Q - (i * m) * P  # Giant step calculation
        if temp in lookup_table:
            return (i * m + lookup_table[temp]) % P.order()  # Compute the discrete log
    
    return None  # If no match is found

if __name__ == "__main__":
    E = EllipticCurve(GF(17), [2, 2])  # Define the elliptic curve over GF(17)
    P = E((5, 1))  # Base point on the curve

    print("Testing Baby-Step Giant-Step Algorithm for ECDLP...\n")
    
    try:
        for i in range(10):  # Test 10 random scalars
            x = random.randint(2, 19)  # Random scalar
            Q = x * P  # Compute Q = xP

            # Compute discrete log using BSGS
            computed_x = bsgs_ecdlp(P, Q, E)

            # Print results
            print(f"Test {i+1}: x = {x}, Computed x = {computed_x}, Q = {Q}")
            
            # Verify correctness
            assert computed_x == x

        print("\n[+] All tests passed successfully!")
    
    except Exception as e:
        print("\n[-] Something's wrong!")
        print(e)
