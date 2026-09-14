# Problem 12: Define a homomorphism between two modules.
def module_homo(M, N):
    if not M in Modules and N in Modules:
        raise ValueError("Must be modules.")

    H = Hom(M, N)
    
    # Get the rank of the domain module
    rank = M.rank()

    # Ask the user to specify the images of the basis vectors
    images = []
    for i in range(rank):
        image = eval(input("Enter the image of the basis vector {}: ".format(i+1)))
        images.append(N(image))

    phi = H(images)
    return(phi)

R = eval(input("Enter a ring: "))
m = eval(input("Enter the dimension of the first module: "))
n = eval(input("Enter the dimension of the second module: "))
M = FreeModule(R, m)
N = FreeModule(R, n)
print(module_homo(M, N))
