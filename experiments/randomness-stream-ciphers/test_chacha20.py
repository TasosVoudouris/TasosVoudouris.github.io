from chacha20 import chacha20_block


def main() -> None:
    # RFC 8439 Section 2.3.2 block-function test vector.
    key = bytes(range(32))
    nonce = bytes.fromhex("000000090000004a00000000")
    block = chacha20_block(key, 1, nonce)
    expected = (
        "10f1e7e4d13b5915500fdd1fa32071c4"
        "c7d1f4c733c068030422aa9ac3d46c4e"
        "d2826446079faa0914c2d705d98b02a2"
        "b5129cd1de164eb9cbd083e8a2503c4e"
    )
    assert block.hex() == expected
    print("ChaCha20 RFC 8439 block vector: PASS")


if __name__ == "__main__":
    main()
