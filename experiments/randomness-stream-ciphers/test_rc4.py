from rc4 import rc4


def main() -> None:
    # Widely used historical RC4 example vector: key="Key", plaintext="Plaintext".
    ct = rc4(b"Key", b"Plaintext")
    assert ct.hex().upper() == "BBF316E8D940AF0AD3"
    assert rc4(b"Key", ct) == b"Plaintext"
    print("RC4 historical vector: PASS")


if __name__ == "__main__":
    main()
