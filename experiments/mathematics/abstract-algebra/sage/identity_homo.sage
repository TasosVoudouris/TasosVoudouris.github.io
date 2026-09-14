# Problem #9: Define a basic (identity) homomorphism between two rings.
def define_homo(R1, R2):
    if R1 not in Rings or R2 not in Rings:
        raise ValueError("Must be rings.")

    H = Hom(R1, R2)
    phi = H([1])
    return(phi)


#### EXAMPLE CODE ####
R1 = eval(input("Enter a ring: "))
R2 = eval(input("Enter another ring: "))
print(define_homo(R1, R2))
