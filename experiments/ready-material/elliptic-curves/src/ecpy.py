import matplotlib.pyplot as plt
import numpy as np


def elliptic_sum(P1, P2):
    """Let a point P = (x, y); let O = (0, np.inf)"""
    x_1, y_1 = P1
    x_2, y_2 = P2
    if y_1 == np.inf:
        return P2
    elif y_2 == np.inf:
        return P1
    elif x_1 == x_2 and y_1 == -y_2:
        return (0, np.inf)  # this is O
    else:
        lam = (y_2 - y_1) / (x_2 - x_1) if P1 != P2 else (3 * (x_1**2) + a) / (2 * y_1)  # the slope
        x_3 = lam**2 - x_1 - x_2
        y_3 = lam * (x_1 - x_3) - y_1
        return (x_3, y_3)
a = -3
b = 5
y, x = np.ogrid[-5:5:100j, -5:5:100j]
z = pow(y, 2) - pow(x, 3) - x * a - b

plt.figure(figsize=(10, 7))
plt.contour(x.ravel(), y.ravel(), z, [0])  # plot the curve y^2 = x^3 + ax + b
plt.grid(True)
plt.title("Elliptic Curve: $y^2 = x^3 + ax + b$")
plt.xlabel("x")
plt.ylabel("y")
plt.axhline(0, color='gray', lw=0.5)
plt.axvline(0, color='gray', lw=0.5)
plt.show()

P1 = (-2.1, pow(pow(-2.1, 3) + -2.1 * a + b, 0.5))
P2 = (0.2, pow(pow(0.2, 3) + 0.2 * a + b, 0.5))
P3 = elliptic_sum(P1, P2)
P3_temp = (P3[0], -P3[1])

# plot the points
plt.figure(figsize=(10, 7))
plt.plot(*P1, "ro")
plt.annotate("P1", xy=P1, xytext=(-5, 5), textcoords="offset points")
plt.plot(*P2, "ro")
plt.annotate("P2", xy=P2, xytext=(-5, 5), textcoords="offset points")
plt.plot(*P3, "ro")
plt.annotate("P1+P2", xy=P3, xytext=(-5, 5), textcoords="offset points")
plt.plot(*P3_temp, "ro")

# plot the lines
plt.plot(
    [P1[0], P3_temp[0]],
    [P1[1], P3_temp[1]],
)
plt.plot(
    [P3[0], P3_temp[0]],
    [P3[1], P3_temp[1]],
)
# plot the curve
plt.grid()
plt.contour(x.ravel(), y.ravel(), pow(y, 2) - pow(x, 3) - x * a - b, [0])
plt.show()