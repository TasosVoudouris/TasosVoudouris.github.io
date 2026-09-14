# Ross-course lattice reconstruction

Clean-room educational reconstructions of the small examples recovered from the 2022 Ross Course on Post-Quantum Cryptography archive.

- `gaussian_integer_ntru.py` shows exact 2D Gaussian reduction and the one-dimensional NTRU analogy `h = g/f (mod q)`.
- `ntru_lll_attack.py` reconstructs the public NTRU lattice for the N=7, p=3, q=41 toy and uses an exact educational LLL implementation to recover a short key equivalent to the original `(f,g)`.

These parameters are deliberately insecure and are useful only for explaining lattice geometry and reduction.
