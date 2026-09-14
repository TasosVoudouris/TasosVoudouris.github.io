# Problem #18: Check if a field extension is normal and/or separable.
def is_normal_extension(F, E):
    for poly in E.defining_polynomial().factor():
        if not all(root in K for root in poly[0].roots(multiplicities=False, ring=K)):
            return False
    return True

def is_separable_extension(F, E):
    defining_polynomial = E.defining_polynomial()
    return defining_polynomial.discriminant() != 0


#### EXAMPLE CODE ####
F = eval(input("Enter a field: "))
E = eval(input("Enter an extension field: "))
print("E is normal over F: " + str(is_normal_extension(F, E)))
print("E is separable over F: " + str(is_separable_extension(F, E)))
