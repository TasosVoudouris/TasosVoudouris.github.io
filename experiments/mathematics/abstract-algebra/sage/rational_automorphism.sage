# Problem #17: Define an automorphism of Q.
def rational_automorphism(F):
    return F.automorphisms()


#### EXAMPLE CODE ####
F = eval(input("Enter a field: "))
print(rational_automorphism(F))
