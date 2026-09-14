"""Evaluate the small Miller-function quotient from the pairing study."""

load("src/pairings/miller_pairing_demo.sage")

value = pairing_quotient_demo()
print("Curve: y^2 = x^3 + 30x + 34 over F_631")
print("Miller-function quotient:", value)
print("Educational parameters only: True")

