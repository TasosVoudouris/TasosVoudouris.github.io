# Problem #5: Define a homomorphish between finite groups.
G = CyclicPermutationGroup(6)
H = CyclicPermutationGroup(3)

def homomorphism_map(g):
    return H(g.order() % 3)

phi = Hom(G, H)([homomorphism_map(g) for g in G.gens()])

a = G.gen()
b = G.gen()^2
print(f"phi(a * b) = {phi(a * b)}")
print(f"phi(a) * phi(b) = {phi(a) * phi(b)}")
