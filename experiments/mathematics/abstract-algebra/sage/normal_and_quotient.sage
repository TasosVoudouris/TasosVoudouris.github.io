# Problem #6: Identify the normal subgroups of a group and define its quotient groups.
def normal_and_quotient(G):
    if not G in Groups:
        raise ValueError("G must be a group.")

    print("Normal subgroups of G:\n")
    for N in G.normal_subgroups():
        print(N)

    print("\nQuotient groups of G:")
    for N in G.normal_subgroups():
        print(G.quotient(N))


#### EXAMPLE CODE ####
G = eval(input("Enter a group in valid SageMath syntax: "))
normal_and_quotient(G)
