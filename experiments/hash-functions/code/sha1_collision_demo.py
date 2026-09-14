"""Verify a published identical-prefix collision for SHA-1.

The differential blocks are historical test data.  Running this file does not
search for a new collision; it verifies that two distinct 320-byte messages
have the same SHA-1 digest and different SHA-256 digests.
"""

from __future__ import annotations

import hashlib


COMMON_PREFIX_HEX = (
    "255044462d312e330a25e2e3cfd30a0a0a312030206f626a0a3c3c2f57696474"
    "682032203020522f4865696768742033203020522f547970652034203020522f"
    "537562747970652035203020522f46696c7465722036203020522f436f6c6f72"
    "53706163652037203020522f4c656e6774682038203020522f42697473506572"
    "436f6d706f6e656e7420383e3e0a73747265616d0affd8fffe00245348412d31"
    "20697320646561642121212121852fec092339759c39b1a1c63c4c97e1fffe01"
)

BLOCK_1_HEX = (
    "7f46dc93a6b67e013b029aaa1db2560b45ca67d688c7f84b8c4c791fe02b3df6"
    "14f86db1690901c56b45c1530afedfb76038e972722fe7ad728f0e4904e046c23"
    "0570fe9d41398abe12ef5bc942be33542a4802d98b5d70f2a332ec37fac3514e7"
    "4ddc0f2cc1a874cd0c78305a21566461309789606bd0bf3f98cda8044629a1"
)

BLOCK_2_HEX = (
    "7346dc9166b67e118f029ab621b2560ff9ca67cca8c7f85ba84c79030c2b3de2"
    "18f86db3a90901d5df45c14f26fedfb3dc38e96ac22fe7bd728f0e45bce046d23"
    "c570feb141398bb552ef5a0a82be331fea48037b8b5d71f0e332edf93ac3500eb4"
    "ddc0decc1a864790c782c76215660dd309791d06bd0af3f98cda4bc4629b1"
)


def colliding_messages() -> tuple[bytes, bytes]:
    prefix = bytes.fromhex(COMMON_PREFIX_HEX)
    return prefix + bytes.fromhex(BLOCK_1_HEX), prefix + bytes.fromhex(BLOCK_2_HEX)


def verify_collision() -> dict[str, str | int | bool]:
    first, second = colliding_messages()
    sha1_first = hashlib.sha1(  # nosec B324 -- intentional historical demo
        first, usedforsecurity=False
    ).hexdigest()
    sha1_second = hashlib.sha1(  # nosec B324
        second, usedforsecurity=False
    ).hexdigest()
    return {
        "length": len(first),
        "messages_differ": first != second,
        "sha1_first": sha1_first,
        "sha1_second": sha1_second,
        "sha1_collision": sha1_first == sha1_second,
        "sha256_collision": hashlib.sha256(first).digest() == hashlib.sha256(second).digest(),
    }


def main() -> None:
    result = verify_collision()
    for key, value in result.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
