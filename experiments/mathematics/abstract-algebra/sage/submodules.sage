# Problem 11: Identify the submodules of a module.
def submodule(M, v):
    if not M in Modules:
        raise ValueError("M must be a module.")
    if not v in M:
        raise ValueError("v must be an element of M.")
    
    N = M.span(v)
    return N

#### EXAMPLE CODE ####
R = eval(input("Enter a ring: "))
n = eval(input("Enter the dimension of the module over the ring: "))
M = FreeModule(R, n)
v = eval(input("Enter a basis to generate a subgroup: "))
print(submodule(M, v))
