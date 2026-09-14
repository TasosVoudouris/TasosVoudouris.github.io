# Audited public-key lab

A small dependency-free reconstruction of the useful algebra from the recovered SageMath coursework.

It intentionally uses tiny parameters and is **not secure cryptographic software**.

The script demonstrates:

- textbook RSA and CRT decryption;
- the RSA common-modulus attack when the same message is used with coprime exponents;
- Diffie–Hellman in a prime-order subgroup;
- textbook ElGamal as the pair `(g^k, m*y^k)`;
- existential forgery of textbook RSA signatures by choosing a signature first.

Several old worksheet mistakes are deliberately not preserved: ignored bit-size parameters, mislabeled ElGamal-as-DH-masking, and noncanonical key-generation logic.
