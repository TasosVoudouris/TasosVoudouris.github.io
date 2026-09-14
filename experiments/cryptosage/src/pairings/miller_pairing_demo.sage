"""Small Miller-function example over F_631.

Based on the supplied `pairing.sage`, whose source comment credited
guan@pku.edu.cn and Example 5.43 of *An Introduction to Mathematical
Cryptography*. The tiny parameters are strictly educational.
"""

PAIRING_FIELD = GF(631)
CURVE_A = PAIRING_FIELD(30)
CURVE_B = PAIRING_FIELD(34)
INFINITY = (None, None)

P5 = (PAIRING_FIELD(36), PAIRING_FIELD(60))
Q5 = (PAIRING_FIELD(121), PAIRING_FIELD(387))
AUXILIARY = (PAIRING_FIELD(0), PAIRING_FIELD(36))


def is_on_demo_curve(point):
    if point == INFINITY:
        return True
    x_coordinate, y_coordinate = point
    return y_coordinate ** 2 == x_coordinate ** 3 + CURVE_A * x_coordinate + CURVE_B


def point_negate(point):
    if point == INFINITY:
        return point
    return point[0], -point[1]


def point_double(point):
    if point == INFINITY or point[1] == 0:
        return INFINITY
    x_coordinate, y_coordinate = point
    slope = (3 * x_coordinate ** 2 + CURVE_A) / (2 * y_coordinate)
    result_x = slope ** 2 - 2 * x_coordinate
    result_y = slope * (x_coordinate - result_x) - y_coordinate
    return result_x, result_y


def point_add(left, right):
    if left == INFINITY:
        return right
    if right == INFINITY:
        return left
    if right == point_negate(left):
        return INFINITY
    if left == right:
        return point_double(left)
    slope = (right[1] - left[1]) / (right[0] - left[0])
    result_x = slope ** 2 - left[0] - right[0]
    result_y = slope * (left[0] - result_x) - left[1]
    return result_x, result_y


def line_quotient(left, right, evaluation_point):
    """Evaluate the Miller line through ``left`` and ``right`` at a point."""

    if left == INFINITY or right == INFINITY:
        return PAIRING_FIELD(1)
    x_eval, y_eval = evaluation_point
    if right == point_negate(left):
        return x_eval - left[0]
    if left == right:
        if left[1] == 0:
            return x_eval - left[0]
        slope = (3 * left[0] ** 2 + CURVE_A) / (2 * left[1])
    else:
        slope = (right[1] - left[1]) / (right[0] - left[0])
    numerator = y_eval - left[1] - slope * (x_eval - left[0])
    sum_point = point_add(left, right)
    if sum_point == INFINITY:
        return numerator
    denominator = x_eval - sum_point[0]
    if denominator == 0:
        raise ZeroDivisionError("evaluation point lies on the Miller denominator")
    return numerator / denominator


def miller_value(base_point, evaluation_point, scalar):
    """Evaluate the Miller function f_(scalar, base_point)."""

    scalar = Integer(scalar)
    if scalar < 1:
        raise ValueError("Miller scalar must be positive")
    bits = bin(int(scalar))[3:]  # omit `0b` and the leading one bit
    accumulator_point = base_point
    function_value = PAIRING_FIELD(1)
    for bit in bits:
        function_value = (
            function_value ** 2
            * line_quotient(
                accumulator_point, accumulator_point, evaluation_point
            )
        )
        accumulator_point = point_double(accumulator_point)
        if bit == "1":
            function_value *= line_quotient(
                accumulator_point, base_point, evaluation_point
            )
            # The supplied file used `T + P`, which concatenated Python lists.
            accumulator_point = point_add(accumulator_point, base_point)
    return function_value


def pairing_quotient_demo():
    """Evaluate f_P(Q + S) / f_P(S) for the supplied five-torsion example."""

    for point in (P5, Q5, AUXILIARY):
        if not is_on_demo_curve(point):
            raise ValueError("invalid textbook example point")
    numerator_point = point_add(Q5, AUXILIARY)
    numerator = miller_value(P5, numerator_point, 5)
    denominator = miller_value(P5, AUXILIARY, 5)
    if denominator == 0:
        raise ZeroDivisionError("unexpected zero Miller denominator")
    return numerator / denominator

