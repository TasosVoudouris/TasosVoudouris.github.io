# Problem 10: Define a module over a ring.
def module_over_ring(R, n):
    if not R in Rings:
        raise ValueError("R must be a ring.")

    M = FreeModule(R, n)
    return M


#### EXAMPLE CODE ####
R = eval(input("Enter a ring: "))
n = eval(input("Enter the dimension of the module over the ring: "))
M = module_over_ring(R, n)
print(M)
print(M.basis())
