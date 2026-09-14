"""Tests for the dependency-free RSA teaching examples."""

import sys
import unittest
from pathlib import Path


SOURCE_DIRECTORY = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SOURCE_DIRECTORY))

from common_modulus_attack import recover_plaintext  # noqa: E402
from low_exponent_attacks import (  # noqa: E402
    hastad_broadcast,
    integer_nth_root,
    recover_unreduced,
)
from shared_prime_attack import recover_shared_factor  # noqa: E402
from textbook_rsa import (  # noqa: E402
    make_keypair,
    private_operation,
    public_operation,
)


class TextbookRsaTests(unittest.TestCase):
    def setUp(self) -> None:
        self.public, self.private = make_keypair(p=61, q=53, e=17)

    def test_documented_example(self) -> None:
        ciphertext = public_operation(65, self.public)
        self.assertEqual(ciphertext, 2790)
        self.assertEqual(private_operation(ciphertext, self.private), 65)

    def test_round_trip_including_nonunits(self) -> None:
        representatives = [0, 1, 53, 61, 65, self.public.n - 1]
        for message in representatives:
            with self.subTest(message=message):
                ciphertext = public_operation(message, self.public)
                self.assertEqual(private_operation(ciphertext, self.private), message)

    def test_representative_range_is_enforced(self) -> None:
        with self.assertRaises(ValueError):
            public_operation(self.public.n, self.public)
        with self.assertRaises(ValueError):
            private_operation(-1, self.private)

    def test_invalid_key_parameters_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            make_keypair(p=61, q=61, e=17)
        with self.assertRaises(ValueError):
            make_keypair(p=61, q=53, e=10)


class AttackExampleTests(unittest.TestCase):
    def test_common_modulus_recovery(self) -> None:
        modulus = 101 * 113
        message = 42
        exponent_1, exponent_2 = 17, 13
        ciphertext_1 = pow(message, exponent_1, modulus)
        ciphertext_2 = pow(message, exponent_2, modulus)
        self.assertEqual(
            recover_plaintext(
                ciphertext_1,
                ciphertext_2,
                exponent_1,
                exponent_2,
                modulus,
            ),
            message,
        )

    def test_common_modulus_requires_coprime_exponents(self) -> None:
        with self.assertRaises(ValueError):
            recover_plaintext(4, 8, 6, 10, 77)

    def test_integer_root_reports_exactness(self) -> None:
        self.assertEqual(integer_nth_root(1234**3, 3), (1234, True))
        root, exact = integer_nth_root(1234**3 + 1, 3)
        self.assertEqual(root, 1234)
        self.assertFalse(exact)

    def test_unreduced_recovery_rejects_nonpower(self) -> None:
        self.assertEqual(recover_unreduced(1234**3, 3), 1234)
        with self.assertRaises(ValueError):
            recover_unreduced(1234**3 + 1, 3)

    def test_hastad_broadcast_recovery(self) -> None:
        message = 123
        exponent = 3
        moduli = [101 * 107, 113 * 131, 137 * 149]
        ciphertexts = [pow(message, exponent, modulus) for modulus in moduli]
        self.assertEqual(
            hastad_broadcast(ciphertexts, moduli, exponent),
            message,
        )

    def test_shared_prime_recovery(self) -> None:
        self.assertEqual(
            recover_shared_factor(101 * 113, 101 * 127),
            101,
        )
        with self.assertRaises(ValueError):
            recover_shared_factor(101 * 113, 107 * 127)


if __name__ == "__main__":
    unittest.main()
