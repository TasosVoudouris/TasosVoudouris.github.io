# Problem #8: Determine whether a polynomial is irreducible in a polynomial ring.
def irreducibility(R, P):
    if not R in Rings:
        raise ValueError("R must be a ring.")
    if not P in R['t']:
        raise ValueError("P must be a polynomial over R.")

    if P.is_irreducible():
        return(f"{P} is irreducible over {R}")
    else:
        return(f"{P} is not irreducible over {R}")


#### EXAMPLE CODE ####
R = eval(input("Enter a ring in valid SageMath syntax: "))
RP.<t> = R['t']
P = RP(input(f"Enter a polynomial of {R} in valid SageMath syntax: "))
print(irreducibility(R, P))
