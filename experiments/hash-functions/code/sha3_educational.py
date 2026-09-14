"""Compact educational SHA3-256 and SHAKE256 implementation.

The byte/lane conversions are intentionally explicit because Keccak's
little-endian lane convention is a frequent source of otherwise subtle bugs.
Use :mod:`hashlib` in production.
"""

from __future__ import annotations


MASK64 = (1 << 64) - 1
ROTATION_OFFSETS = (
    (0, 36, 3, 41, 18),
    (1, 44, 10, 45, 2),
    (62, 6, 43, 15, 61),
    (28, 55, 25, 21, 56),
    (27, 20, 39, 8, 14),
)
ROUND_CONSTANTS = (
    0x0000000000000001, 0x0000000000008082,
    0x800000000000808A, 0x8000000080008000,
    0x000000000000808B, 0x0000000080000001,
    0x8000000080008081, 0x8000000000008009,
    0x000000000000008A, 0x0000000000000088,
    0x0000000080008009, 0x000000008000000A,
    0x000000008000808B, 0x800000000000008B,
    0x8000000000008089, 0x8000000000008003,
    0x8000000000008002, 0x8000000000000080,
    0x000000000000800A, 0x800000008000000A,
    0x8000000080008081, 0x8000000000008080,
    0x0000000080000001, 0x8000000080008008,
)


def _rotl64(value: int, count: int) -> int:
    count %= 64
    if count == 0:
        return value & MASK64
    return ((value << count) | (value >> (64 - count))) & MASK64


def keccak_f1600(state: list[int]) -> None:
    """Permute 25 64-bit lanes in place using 24 Keccak-f rounds."""

    if len(state) != 25:
        raise ValueError("Keccak-f[1600] has 25 lanes")
    for round_constant in ROUND_CONSTANTS:
        # theta: mix the parity of each column into its two neighbours.
        parity = [
            state[x] ^ state[x + 5] ^ state[x + 10] ^ state[x + 15] ^ state[x + 20]
            for x in range(5)
        ]
        for x in range(5):
            delta = parity[(x - 1) % 5] ^ _rotl64(parity[(x + 1) % 5], 1)
            for y in range(5):
                state[x + 5 * y] ^= delta

        # rho and pi: rotate each lane and move it to a new coordinate.
        moved = [0] * 25
        for x in range(5):
            for y in range(5):
                destination_x = y
                destination_y = (2 * x + 3 * y) % 5
                moved[destination_x + 5 * destination_y] = _rotl64(
                    state[x + 5 * y], ROTATION_OFFSETS[x][y]
                )

        # chi: the only nonlinear step; process each row from an unchanged copy.
        for y in range(5):
            row = [moved[x + 5 * y] for x in range(5)]
            for x in range(5):
                state[x + 5 * y] = (
                    row[x] ^ ((~row[(x + 1) % 5]) & row[(x + 2) % 5])
                ) & MASK64

        # iota: break round symmetry.
        state[0] ^= round_constant


def _pad(message: bytes, rate_bytes: int, suffix: int) -> bytes:
    """Apply Keccak's delimited suffix and multi-rate pad10*1 padding."""

    if not 0 < suffix < 256:
        raise ValueError("suffix must fit in one nonzero byte")
    padded = bytearray(message)
    padded.append(suffix)
    padded.extend(b"\x00" * ((-len(padded)) % rate_bytes))
    padded[-1] ^= 0x80
    return bytes(padded)


def sponge(message: bytes, rate_bits: int, suffix: int, output_length: int) -> bytes:
    """Absorb, permute and squeeze a Keccak-f[1600] sponge."""

    if rate_bits % 64 or not 0 < rate_bits < 1600:
        raise ValueError("this implementation requires a lane-aligned rate")
    if output_length < 0:
        raise ValueError("output_length cannot be negative")
    rate_bytes = rate_bits // 8
    state = [0] * 25
    padded = _pad(message, rate_bytes, suffix)

    for block_start in range(0, len(padded), rate_bytes):
        block = padded[block_start : block_start + rate_bytes]
        for offset in range(0, rate_bytes, 8):
            state[offset // 8] ^= int.from_bytes(block[offset : offset + 8], "little")
        keccak_f1600(state)

    output = bytearray()
    while len(output) < output_length:
        rate_view = b"".join(lane.to_bytes(8, "little") for lane in state[: rate_bytes // 8])
        output.extend(rate_view[: output_length - len(output)])
        if len(output) < output_length:
            keccak_f1600(state)
    return bytes(output)


def sha3_256(message: bytes) -> bytes:
    """FIPS 202 SHA3-256: rate 1088, capacity 512, suffix 0x06."""

    return sponge(message, rate_bits=1088, suffix=0x06, output_length=32)


def shake256(message: bytes, output_length: int) -> bytes:
    """FIPS 202 SHAKE256: rate 1088, capacity 512, suffix 0x1f."""

    return sponge(message, rate_bits=1088, suffix=0x1F, output_length=output_length)


def main() -> None:
    import hashlib

    for message in (b"", b"abc", b"a" * 135, b"a" * 136, b"a" * 137):
        ours = sha3_256(message)
        reference = hashlib.sha3_256(message).digest()
        print(f"length={len(message):3d} match={ours == reference} digest={ours.hex()}")


if __name__ == "__main__":
    main()
