# Problem 3: Find all subgroups of an arbitrary abelian group
def find_subgroups(G):
    if not G in Groups:
        return("Please select a finite abelian group.")
    elif not G.is_abelian() or not G.is_finite():
        return("Please select a finite abelian group.")

    sgs = G.subgroups()

    for sg in sgs:
        print("Subgroup: " + str(sg))
        print("Order: " + str(sg.order()))
        print("\n")

    return(sgs)

