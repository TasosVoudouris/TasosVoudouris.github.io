# Problem 14: Find the splitting field of a polynomial
def splitting_field(F, p):
    if not F in Fields:
        raise ValueError("F must be a field.")

    R.<x> = PolynomialRing(F)
    p = R(p)
    if not p in R:
        raise ValueError("Must pass a polynomial over the field F.")

    K = p.splitting_field('a')
    return K


#### EXAMPLE CODE ####
F = eval(input("Enter a field: "))
p = input("Enter a polynomial over the field: ")
print(splitting_field(F, p))
