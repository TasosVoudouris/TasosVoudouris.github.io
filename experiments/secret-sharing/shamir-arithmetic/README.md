# Shamir arithmetic and degree growth

Run:

```bash
python demo.py
```

The script demonstrates the exact invariant discussed in the companion article:
addition preserves the sharing degree, pointwise multiplication adds degrees, and
continuing an MPC computation requires a degree-reduction/resharing mechanism.

`trusted_degree_reduce()` is intentionally insecure: it reconstructs to a trusted
dealer and only exists to make the algebra visible.
