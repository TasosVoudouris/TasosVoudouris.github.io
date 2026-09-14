"""RFC 8439 ChaCha20 block function, for study and test-vector validation."""
import struct

MASK32 = 0xFFFFFFFF


def rotl32(x: int, n: int) -> int:
    return ((x << n) & MASK32) | (x >> (32 - n))


def quarter_round(s: list[int], a: int, b: int, c: int, d: int) -> None:
    s[a] = (s[a] + s[b]) & MASK32; s[d] ^= s[a]; s[d] = rotl32(s[d], 16)
    s[c] = (s[c] + s[d]) & MASK32; s[b] ^= s[c]; s[b] = rotl32(s[b], 12)
    s[a] = (s[a] + s[b]) & MASK32; s[d] ^= s[a]; s[d] = rotl32(s[d], 8)
    s[c] = (s[c] + s[d]) & MASK32; s[b] ^= s[c]; s[b] = rotl32(s[b], 7)


def chacha20_block(key: bytes, counter: int, nonce: bytes) -> bytes:
    if len(key) != 32 or len(nonce) != 12:
        raise ValueError("RFC 8439 uses a 32-byte key and 12-byte nonce")
    constants = b"expand 32-byte k"
    state = list(struct.unpack("<4I", constants))
    state += list(struct.unpack("<8I", key))
    state += [counter & MASK32]
    state += list(struct.unpack("<3I", nonce))
    working = state.copy()
    for _ in range(10):
        quarter_round(working, 0, 4, 8, 12)
        quarter_round(working, 1, 5, 9, 13)
        quarter_round(working, 2, 6, 10, 14)
        quarter_round(working, 3, 7, 11, 15)
        quarter_round(working, 0, 5, 10, 15)
        quarter_round(working, 1, 6, 11, 12)
        quarter_round(working, 2, 7, 8, 13)
        quarter_round(working, 3, 4, 9, 14)
    out = [(x + y) & MASK32 for x, y in zip(working, state)]
    return struct.pack("<16I", *out)
