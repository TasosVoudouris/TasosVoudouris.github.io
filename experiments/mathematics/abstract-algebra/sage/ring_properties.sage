# Problem #7: Verify basic ring properties of a space, set, group, or ring.
def verify_properties(R):
    if not R in Rings:
        raise ValueError("R must be a ring.")

    print("Is a ring:      " + str(R.is_ring()))
    print("Has identity:   " + str(has_one(R)))
    print("Is commutative: " + str(R.is_commutative()))
    print("Is a domain:    " + str(R in IntegralDomains))
    print("Is a UFD:       " + str(R in UniqueFactorizationDomains))
    print("Is a PID:       " + str(R in PrincipalIdealDomains))
    print("is a ED:        " + str(R in EuclideanDomains))
    print("Is a field:     " + str(R in Fields))


def has_one(R):
    if not R in Rings:
        raise ValueError("R must be a ring.")

    try:
        R.one()
        return True
    except:
        return False


#### EXAMPLE CODE ####
R = eval(input("Enter a ring in valid SageMath syntax: "))
verify_properties(R)
