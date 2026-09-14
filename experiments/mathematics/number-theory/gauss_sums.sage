# ============================================================================
# Gauss Sums and Jacobi Sums in Finite Fields
# ============================================================================
# This script computes the n-th power of a Gauss sum g(c)^n for a Dirichlet
# character c of order n over the finite field F_p^*. It verifies the identity:
#
#   g(c)^n = c(-1) * p * J(c, c) * J(c, c^2) * ... * J(c, c^(n-2))
#
# See: Ireland & Rosen, *A Classical Introduction to Modern Number Theory*
# ============================================================================

# Select a prime modulus
p = 5

# Construct the Dirichlet group modulo p
G = DirichletGroup(p)
print(f"Number of characters: {len(G)} (should be p - 1 = {p - 1})\n")

# Choose a character c of order n from the group
k = 1  # 0 <= k <= p - 2
c = G[k]
n = c.order()
print(f"Selected character #{k}: {c}")
print(f"Order of the character: {n}\n")

# Compute the right-hand side (RHS) of the identity
# RHS = c(-1) * p * product of Jacobi sums J(c, c^i) for i = 1 to n - 2
JP = c(-1) * p
for i in range(1, n - 1):
    JP *= c.jacobi_sum(c**i)

print(f"RHS (Jacobi product): {JP}\n")

# Compute the left-hand side (LHS): g(c)^n
GS = c.gauss_sum()
print(f"Gauss sum g(c): {GS}")
print(f"LHS g(c)^n: {GS^n}")

# Verify the identity
if GS^n == JP:
    print("Success: LHS == RHS\n")
else:
    print("Warning: LHS != RHS (not formally equal)\n")

# ============================================================================
# Visualize Gauss and Jacobi Sums in the Complex Plane
# ============================================================================

# Plot both GS and JP on the complex plane
a = plot([], figsize=(3, 3), title='Gauss and Jacobi Sums',
         frame=True, axes_labels=['$x$-axis', '$y$-axis'])
a += list_plot([JP], color='red', size=30, legend_label='JP (Jacobi product)')
a += list_plot([GS], color='blue', size=10, legend_label='GS (Gauss sum)')
a.save('gauss_jacobi_plot.png')  


# Plot JP and GS^n on the complex plane
a = plot([], figsize=(3, 3), title='Gauss^n vs Jacobi Product',
         frame=True, axes_labels=['$x$-axis', '$y$-axis'])
a += list_plot([JP], color='red', size=30, legend_label='JP (Jacobi product)')
a += list_plot([GS^n], color='blue', size=10, legend_label='GS^n')
show(a)

# Confirm equality via ratio
print("Ratio JP / g(c)^n =", JP / GS^n)  # Should print 1
