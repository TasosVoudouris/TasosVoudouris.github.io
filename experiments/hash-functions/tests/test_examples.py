"""Regression tests for every executable Python lab."""

from __future__ import annotations

import hashlib
import hmac
import pathlib
import sys
import unittest


CODE = pathlib.Path(__file__).resolve().parents[1] / "code"
sys.path.insert(0, str(CODE))

from birthday_collision import (  # noqa: E402
    birthday_approximation,
    collision_probability,
    find_collision,
    truncated_sha256,
)
from length_extension_demo import forge_sha256_secret_prefix_mac  # noqa: E402
from mac_examples import tag_request, verify_request  # noqa: E402
from sha1_collision_demo import verify_collision  # noqa: E402
from sha256_educational import sha256  # noqa: E402
from sha3_educational import sha3_256, shake256  # noqa: E402


class BirthdayTests(unittest.TestCase):
    def test_truncation_preserves_width(self) -> None:
        self.assertLess(truncated_sha256(b"leading-zero-test", 13), 1 << 13)

    def test_collision_search(self) -> None:
        collision = find_collision(bits=12)
        self.assertNotEqual(collision.first, collision.second)
        self.assertEqual(
            truncated_sha256(collision.first, 12),
            truncated_sha256(collision.second, 12),
        )

    def test_exact_and_approximate_probabilities(self) -> None:
        exact = collision_probability(100, 16)
        approximate = birthday_approximation(100, 16)
        self.assertAlmostEqual(exact, approximate, delta=0.001)


class SHA1CollisionTests(unittest.TestCase):
    def test_historical_collision(self) -> None:
        result = verify_collision()
        self.assertTrue(result["messages_differ"])
        self.assertTrue(result["sha1_collision"])
        self.assertFalse(result["sha256_collision"])


class SHA256Tests(unittest.TestCase):
    def test_standard_vectors_and_boundaries(self) -> None:
        messages = (b"", b"abc", b"a" * 55, b"a" * 56, b"a" * 64, b"a" * 1000)
        for message in messages:
            with self.subTest(length=len(message)):
                self.assertEqual(sha256(message), hashlib.sha256(message).digest())

    def test_length_extension(self) -> None:
        secret = b"unknown-secret"
        original = b"role=user"
        suffix = b"&role=admin"
        known_tag = hashlib.sha256(secret + original).digest()
        forgery = forge_sha256_secret_prefix_mac(
            original, known_tag, suffix, guessed_secret_length=len(secret)
        )
        expected = hashlib.sha256(secret + forgery.message).digest()
        self.assertTrue(hmac.compare_digest(forgery.tag, expected))


class SHA3Tests(unittest.TestCase):
    def test_sha3_vectors_and_rate_boundaries(self) -> None:
        for message in (b"", b"abc", b"a" * 135, b"a" * 136, b"a" * 137):
            with self.subTest(length=len(message)):
                self.assertEqual(sha3_256(message), hashlib.sha3_256(message).digest())

    def test_shake_multi_block_output(self) -> None:
        self.assertEqual(shake256(b"abc", 200), hashlib.shake_256(b"abc").digest(200))


class MACTests(unittest.TestCase):
    def test_authentication_and_tampering(self) -> None:
        key = bytes(range(32))
        body = b"amount=100"
        tag = tag_request(key, "POST", "/transfer", body)
        self.assertTrue(verify_request(key, "POST", "/transfer", body, tag))
        self.assertFalse(verify_request(key, "POST", "/transfer", body + b"0", tag))


if __name__ == "__main__":
    unittest.main()
