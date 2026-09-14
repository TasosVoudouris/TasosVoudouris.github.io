# NTT engineering mini-demo

A small independent radix-2 NTT/INTT over `F_97` used to validate the equations in
the article without copying the much larger recovered package.

```bash
python ntt_demo.py
```

The source batch also contained a q=12289 iterative/recursive implementation. Its
core tests were audited separately; see `site-planning/secret-sharing-cleanup.md`.
