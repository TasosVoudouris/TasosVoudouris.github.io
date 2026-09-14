# ====================================================================
# 1) Addition on the unit circle in QQ
# ====================================================================
# Create polynomial generators x, y over QQ
x, y = polygen(QQ, 'x, y')
# Define the unit circle curve y^2 + x^2 = 1
unit_circle = Curve(y**2 + x**2 - 1)

def add_circle(P1, P2):
    """
    Add two points on the unit circle using complex-number interpretation:
      (x1, y1) + (x2, y2)  ↔  (x1 y2 + y1 x2, y1 y2 − x1 x2)
    """
    x1, y1 = P1
    x2, y2 = P2
    return (x1 * y2 + y1 * x2, y1 * y2 - x1 * x2)

# Two example rational points on the unit circle
P1 = (3/5, 4/5)
P2 = (5/13, 12/13)
P3 = add_circle(P1, P2)

# Check that adding (0,1) acts as identity
print("P1 + (0,1) = P1? →", P1 == add_circle(P1, (0, 1)))  # prints True

# Plot the circle and highlight P1, P2, P3
graphic = plot(unit_circle)  
graphic += point(P1, size=50, color='red',   legend_label='P1')
graphic += point(P2, size=50, color='green', legend_label='P2')
graphic += point(P3, size=50, color='cyan',  legend_label='P3')
# Save to file
graphic.save("unit_circle_plot.png")


# ====================================================================
# 2) Visualizing various “original” Edwards‐type curves
#    x^2 + y^2 = c^2 + c^2 x^2 y^2
# ====================================================================
c1, c2, c3 = 0, 2, 5  # you can tweak these constants
ed1 = Curve(y**2 + x**2 - c1**2 - c1**2 * x**2 * y**2)
ed2 = Curve(y**2 + x**2 - c2**2 - c2**2 * x**2 * y**2)
ed3 = Curve(y**2 + x**2 - c3**2 - c3**2 * x**2 * y**2)

# Plot all three on the same axes (different colors)
graphic = ed1.plot() \
        + ed2.plot(color='red') \
        + ed3.plot(color='green')
graphic.save("curve1.png")


# ====================================================================
# 3) Standard Edwards addition over a finite field GF(19)
# ====================================================================
# Set up the field and curve parameter d
x, y = polygen(GF(19), 'x, y')
d = -30
# Standard form: x^2 + y^2 = 1 + d x^2 y^2
ed  = Curve(y**2 + x**2 - 1 - d * x**2 * y**2)

# Pick two points from the curve’s F₁₉-rational point set
points = ed.point_set().points()
P1, P2 = points[15], points[12]  
# Compute their Edwards-sum
def add_edwards(P1, P2):
    """
    Edwards addition formula:
      x₃ = (x1 y2 + y1 x2) / (1 + d x1 x2 y1 y2)
      y₃ = (y1 y2 − x1 x2) / (1 − d x1 x2 y1 y2)
    """
    x1, y1 = P1
    x2, y2 = P2
    num_x = x1*y2 + y1*x2
    num_y = y1*y2 - x1*x2
    den_x = 1 + d*x1*x2*y1*y2
    den_y = 1 - d*x1*x2*y1*y2
    return (num_x/den_x, num_y/den_y)

P3 = add_edwards(P1, P2)
print("P1 + P2 =", P3)  # prints (3, 14)

# Plot all F₁₉-points and highlight P1, P2, P3
graphic = point(points)
graphic += point([P1], size=50, color='red',   legend_label=f'P1 = {P1}')
graphic += point([P2], size=50, color='green', legend_label=f'P2 = {P2}')
graphic += point([P3], size=50, color='cyan',  legend_label=f'P3 = {P3}')
graphic.save("curve2.png")


# ====================================================================
# 4) Exploring the “simplified” new family of Edwards‐type curves
#    y^2 + a x^2 = 1 + d x^2 y^2
# ====================================================================
x, y = polygen(QQ, 'x, y')
# Play with these parameters
a1, a2, a3 = 1, 2, 10
d1, d2, d3 = 6, -10, -100

ed1 = Curve(y**2 + a1*x**2 - 1 - d1*x**2*y**2)
ed2 = Curve(y**2 + a2*x**2 - 1 - d2*x**2*y**2)
ed3 = Curve(y**2 + a3*x**2 - 1 - d3*x**2*y**2)

# Plot and restrict axes for clarity
graphic = plot(ed1) \
        + plot(ed2, color='red') \
        + plot(ed3, color='green')
graphic.set_axes_range(xmin=-3, xmax=3, ymin=-3, ymax=3)
graphic.save("curve3.png")
