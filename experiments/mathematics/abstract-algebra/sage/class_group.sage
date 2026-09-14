# Problem #20: Find the class group of a ring of integers of a rational field extension.
f = input("Enter a polynomial over Q: ")
R.<x> = PolynomialRing(QQ)
f = R(f)
K = NumberField(f, 'a')

ring_of_integers = K.ring_of_integers()

class_group = ring_of_integers.class_group()

print("Number Field:", K)
print("Ring of Integers:", ring_of_integers)
print("Class Group:", class_group)
print("Class Number:", class_group.order())
