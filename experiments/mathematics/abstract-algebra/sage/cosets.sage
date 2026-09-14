# Problem #4: Verify Lagrange's Theorem for an arbitrary group.
def verify_Lagrange(G, H):
    if not H in G.subgroups():
        raise ValueError("H should be a subgroup of G.")

    cosets = G.cosets(H)
    for i in range(len(cosets)):
        if cosets[i] not in cosets[:i]:
            print("Unique coset #" + str(i+1) + ": " + str(cosets[i]))
        else:
            print("Error! Math is broken!")


#### EXAMPLE CODE ####
G = eval(input("Enter a group in valid SageMath syntax:     "))
H = eval(input("Enter a subgroup in valid SageMath syntax:  "))
verify_Lagrange(G, H)
