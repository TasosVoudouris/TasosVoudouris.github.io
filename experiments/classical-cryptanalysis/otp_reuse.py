"""Demonstrate the algebraic failure caused by reusing a one-time-pad/stream key."""


def xor(a: bytes, b: bytes) -> bytes:
    return bytes(x ^ y for x, y in zip(a, b))


def demo():
    m1 = b"attack at dawn"
    m2 = b"retreat at now"
    key = b"correct horse!"  # same length as the messages, reused on purpose
    c1 = xor(m1, key)
    c2 = xor(m2, key)
    assert xor(c1, c2) == xor(m1, m2)
    known_m1 = m1
    recovered_m2 = xor(xor(c1, c2), known_m1)
    assert recovered_m2 == m2
    print("key reuse exposed m1 XOR m2 and recovered the second message from known plaintext")


if __name__ == "__main__":
    demo()
