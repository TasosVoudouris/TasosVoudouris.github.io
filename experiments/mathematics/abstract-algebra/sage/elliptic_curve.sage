# Problem #19: Define an elliptic curve over a field.
F = eval(input("Enter a field: "))
a = float(input("Enter a: "))
b = float(input("Enter b: "))

print(EllipticCurve(F, [a, b]))
