# SPDZ authenticated-share invariant toy

```bash
python demo.py
```

The demo validates `gamma = alpha * x`, linearity, Beaver multiplication, and a
simple tamper-detection case. The dealer/checker sees `alpha`; real SPDZ keeps the
MAC key secret-shared and runs a distributed MAC check.
