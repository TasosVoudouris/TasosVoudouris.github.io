---
sidebar_position: 3
---

# Foundations and helpers

The shared code separates three operations that were previously scattered
across the examples: conversion to bytes, hashing/KDF expansion, and elliptic-
curve point handling.

## Hashing

The compatibility digest maps a message to a non-negative Sage integer:

```python
def digest(message):
    encoded = to_bytes(message)
    return Integer(hashlib.sha1(encoded).hexdigest(), 16)
```

SHA-1 is retained because the original demonstrations and RFC-era material were
written around a 160-bit digest. New protocol designs should use SHA-256 or a
newer approved hash and should define domain separation and serialization
explicitly.

## Integer and point encoding

`i2osp` implements the integer-to-octet-string primitive. A point is encoded as
the fixed-width concatenation of its affine coordinates:

```python
def point_to_bytes(point, coordinate_size):
    x_coordinate, y_coordinate = point.xy()
    return i2osp(x_coordinate, coordinate_size) + i2osp(
        y_coordinate, coordinate_size
    )
```

This uncompressed educational representation is unambiguous when the coordinate
size is fixed. Standards normally add a format byte and define compressed and
uncompressed encodings precisely.

## KDF and symmetric helpers

The reviewed KDF expands SHA-256 in counter mode and returns an explicit number
of raw bytes. EC encryption uses separate encryption and MAC keys. PKCS#7
padding and unpadding replace the original zero padding, which could not recover
messages ending in zero bytes unambiguously.

The helper functions centralize input validation, but they do not make the
demonstrations constant-time.
