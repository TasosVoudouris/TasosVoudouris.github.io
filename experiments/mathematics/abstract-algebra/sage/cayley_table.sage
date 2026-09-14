# Problem 1: Print the Cayley table of an arbitrary group.
def cayley_table(G):
    order = G.order()
    table = [G.list()]
    for i in range(1, order):
        row = []
        for j in range(0, order):
            row.append(G.list()[i] * G.list()[j])
        table.append(row)

    return(table)

def print_table(table):
    max_width = max(len(str(item)) for row in table for item in row)

    for row in table:
        for item in row:
            print(f"{str(item):^{max_width}}", end=" ")
        print("\n")


#### TEST CODE ####
G = eval(input("Please enter a group in valid SageMath syntax: "))
while not G in Groups:
    G = eval(input("Please enter a group in valid SageMath syntax: "))
    print("Group is invalid. Please enter a valid group.")
table = cayley_table(G)
print_table(table)
