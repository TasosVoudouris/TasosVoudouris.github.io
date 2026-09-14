# Problem 2: Find the order of an arbitrary finite abelian group.
def find_order(G):
    if not G in Groups:
        return("Please select a finite abelian group.")
    elif not G.is_abelian() or not G.is_finite():
        return("Please select a finite abelian group.")

    order = 1
    for gen in G.gens():
        order = order *gen.order()

    return(order)
