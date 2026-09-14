# Discrete Logarithm Attack Comparison on a Tiny Elliptic Curve

This repo compares the performance of three classical algorithms for solving the Elliptic Curve Discrete Logarithm Problem (ECDLP):

- `bruteforce`
- `babygiantstep`
- `pollardsrho`

We use a toy elliptic curve defined as follows:

```python
tinycurve = EllipticCurve(
    p=10177,            # Prime field
    a=1,                # Curve parameter a
    b=-1,               # Curve parameter b
    g=(1, 1),           # Generator point G
    n=10331,            # Order of the group
```
Execute the  `performance_comparison.py`. 