# Quarantined original VSS source

The files under `vss-example-source-sanitized/` are selected offline scripts
copied unchanged from the uploaded research archive. They are retained so the
Version 0.5 corrections can be compared with the original ideas.

They are **not** imported by the active package and are **not** validated
implementations. Several require unavailable third-party packages, and the BLS,
KZG, and multiprocess examples contain protocol errors described in
[`../ARCHIVE_AUDIT.md`](../ARCHIVE_AUDIT.md).

Original uploaded ZIP SHA-256:

```text
bd128f12bb5a25a965c86230d47eca6ce4048b26104034e61302833f6ecf71b7
```

The following material was intentionally not copied:

- `server.key`, because it is a private key and must be treated as compromised;
- `server.crt`, because it is expired and belongs to the unsafe TLS experiment;
- `client.py`, `server.py`, `generate_cert.py`, and MQTT scripts, to prevent
  accidental execution of insecure network examples;
- the nested third-party source tree, because the supplied copy has no clear
  license file;
- bytecode caches, screenshots, and the bundled PDF.

Do not run the quarantined scripts as part of Version 0.5. Use the files in
`../cryptocave_sss/` and `../examples/` instead.
