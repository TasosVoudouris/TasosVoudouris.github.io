# Mathematics.zip cleanup and consolidation — v6.4

This document records the consolidation of the uploaded pure-mathematics batch into the canonical CryptoCave repository.

## Source accounting

- Original source archive: `Mathematics.zip`
- Original files: **270**
- Ledger rows: **270**
- Unclassified files: **0**
- SHA-256: `e523528d8a76c41d7f699894fd9b33c50ec2de42209a043f3ab1fd624315ac6e`
- Exact source archive retained only in the FULL master at `.local-reference-library/source-batches/Mathematics.zip`

Disposition totals:

- **85** integrated/reworked into canonical mathematics content or selected companion material;
- **35** superseded by stronger canonical CryptoCave articles;
- **117** retained only as reference/provenance inside the exact source batch;
- **30** generated artifacts discarded from the active tree (checkpoints, bytecode, generated Sage translations, OS metadata);
- **2** empty placeholders discarded;
- **1** obsolete local navigation file superseded by the canonical content map.

The machine-readable decision ledger is `site-planning/mathematics-source-ledger.csv`.

## Canonical architecture created from the batch

### Elementary Number Theory Reference

The previous `Number Theory & Algebra Reference` name was narrowed to **Elementary Number Theory Reference**. Its existing nine articles remain the arithmetic/congruence/primality foundation. General abstract algebra was separated rather than continuing to mix groups/rings/fields into the same path.

### Abstract Algebra Foundations — 7 parts

1. Groups, subgroups, cyclic structure, and element order.
2. Homomorphisms, kernels, cosets, normal subgroups, and quotients.
3. Rings, ideals, integral domains, and quotient rings.
4. Fields, algebraic extensions, splitting fields, and automorphisms.
5. Polynomial rings, irreducibility, quotients, and splitting fields.
6. Modules over rings as the bridge from vector spaces to lattices.
7. Polynomial ideals, affine varieties, and coordinate rings.

### Finite Fields & Polynomial Arithmetic — 4 parts

1. Construction from prime fields to extension fields.
2. Frobenius, trace, norm, and subfields.
3. Irreducible polynomials and explicit extension-field construction.
4. Root finding and polynomial factorization over finite fields.

### Computational Number Theory — 7 parts

1. Multiplicative functions and Dirichlet convolution.
2. Prime counting, the Prime Number Theorem, and prime gaps.
3. Gaussian integers and Euclidean division.
4. Dirichlet characters and Gauss sums.
5. Jacobi sums, cyclotomy, and character-based point counting.
6. Binary quadratic forms, class groups, and norm equations.
7. Integer factorization from Fermat/Pollard through ECM, QS, and NFS.

### Linear Algebra & Lattices — 4 parts

1. Vectors, matrices, linear maps, and vector spaces.
2. Gram–Schmidt, projections, determinants, and volume.
3. Integer lattices, basis equivalence, determinant, and duals.
4. LLL reduction and the Lovász condition.

### Elliptic Curve Mathematics — 13 parts

The old EC series mixed pure mathematics with attacks. v6.4 makes the mathematical progression explicit:

1. Plane cubics, projective closure, and nonsingularity.
2. Weierstrass curves and the group law.
3. Why the group law is associative.
4. Rational points, heights, descent, and Mordell–Weil.
5. Torsion points and Nagell–Lutz.
6. Curves over finite fields, Hasse, and Frobenius.
7. Curve models, isomorphisms, and the j-invariant.
8. Montgomery curves and the Montgomery ladder.
9. Edwards and twisted Edwards curves.
10. Division polynomials and n-torsion.
11. Divisors, Weil pairing, and Tate pairing.
12. Schoof point counting.
13. Isogenies, modular polynomials, and CM arithmetic.

### Elliptic Curve Cryptanalysis — 3 parts

The attack-oriented material was moved out of the mathematics path:

1. Singular-curve DLP reductions.
2. MOV pairing reduction.
3. Smart's attack on anomalous curves.

### Discrete Logarithm Algorithms

Index calculus in finite fields was added as Part V because that material belongs with DLP algorithms, not with the pure mathematics reading path.

## Corrections applied

The consolidation deliberately corrected mathematical mistakes rather than preserving them verbatim. Examples include:

- the group identity law is `ae = ea = a`, not `e`;
- full `n`-torsion has the usual `(Z/nZ)^2` structure over an algebraic closure when the characteristic does not divide `n`; this is not automatically the structure of `E(K)[n]` over an arbitrary base field;
- supersingularity was described using Frobenius trace/p-torsion with the proper characteristic qualifications;
- finite fields are unique **up to isomorphism**, not as a literal canonical set;
- absence of roots proves irreducibility only for degrees 2 and 3, not arbitrary degree;
- the Riemann-Hypothesis-strength prime-counting error term is explicitly conditional;
- the old Gaussian-integer quotient code was replaced by nearest-lattice-point Euclidean division;
- “Rabin root finding,” irreducibility testing, and complete finite-field factorization were separated terminologically;
- LLL is presented as polynomial-time lattice reduction with an approximation guarantee, not as an exact polynomial-time SVP solver;
- Montgomery-ladder regularity is not equated automatically with constant-time implementation security.

## Source/reference policy

Large third-party course archives, papers, old EC attack repositories, repeated DLP/RSA notebooks, MIT/Sutherland material, Sage worksheets, and generated notebook/checkpoint artifacts were **not** copied into the active Git tree.

Their exact bytes remain recoverable from the one retained source archive in the FULL master. The active repository keeps only canonical prose and selected companion programs.
