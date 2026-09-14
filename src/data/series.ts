export const SERIES_NAMES = [
	'Cryptography Primer',
	'Cryptography From Zero',
	'Classical Cryptanalysis',
	'Elementary Number Theory Reference',
	'Abstract Algebra Foundations',
	'Finite Fields & Polynomial Arithmetic',
	'Computational Number Theory',
	'Linear Algebra Foundations',
	'Lattices & Lattice-Based Cryptography',
	'Symmetric Cryptography',
	'Hash Functions & MACs',
	'Randomness & Stream Ciphers',
	'Discrete Logarithm Algorithms',
	'Diffie–Hellman & ElGamal',
	'Elliptic Curve Mathematics',
	'Elliptic Curve Cryptanalysis',
	'Digital Signatures',
	'Secret Sharing & Polynomial Tools',
	'Secure Multiparty Computation',
	'Threshold Cryptography Engineering',
	'Oblivious Transfer',
	'Homomorphic Encryption',
	'Zero-Knowledge Proof Systems',
	'RSA Deep Dives',
] as const;

export type SeriesName = (typeof SERIES_NAMES)[number];

export type SeriesGroup =
	| 'Start Here'
	| 'Mathematical Foundations'
	| 'Core Cryptography'
	| 'Public-Key & Algebraic Systems'
	| 'Distributed Cryptography'
	| 'Privacy-Preserving Computation'
	| 'Security Analysis';

export type SeriesDefinition = {
	name: SeriesName;
	slug: string;
	shortDescription: string;
	description: string;
	startLabel: string;
	group: SeriesGroup;
};

export const SERIES_GROUPS: readonly SeriesGroup[] = [
	'Start Here',
	'Mathematical Foundations',
	'Core Cryptography',
	'Public-Key & Algebraic Systems',
	'Distributed Cryptography',
	'Privacy-Preserving Computation',
	'Security Analysis',
];

export const SERIES: readonly SeriesDefinition[] = [
	{name:'Cryptography Primer',slug:'cryptography-primer',shortDescription:'Orientation, bit-level tools, encodings, randomness, and Python/SageMath vocabulary.',description:'A preparation path before the main mathematical sequence: security vocabulary, logical and encoding operations, practical Python/SageMath tools, and cryptographic randomness.',startLabel:'Start the primer',group:'Start Here'},
	{name:'Cryptography From Zero',slug:'cryptography-from-zero',shortDescription:'A sequential path from executable arithmetic to Diffie–Hellman and RSA.',description:'The main beginner-first path: Python experiments, arithmetic and algebra, Diffie–Hellman, implementation-security examples, CRT, primality, and RSA key generation.',startLabel:'Start from 00',group:'Start Here'},
	{name:'Classical Cryptanalysis',slug:'classical-cryptanalysis',shortDescription:'Frequency analysis, audited classical-cipher code, Vigenère/Kasiski reasoning, and one-time-pad or stream-key reuse.',description:'A compact historical attack path showing how structure leaks through classical systems: Caesar/substitution analysis, an audited SageMath lab covering affine/Hill algebra and implementation mistakes, Kasiski examination of Vigenère, and XOR/crib-dragging failures from pad reuse.',startLabel:'Start with frequency analysis',group:'Security Analysis'},
	{name:'Elementary Number Theory Reference',slug:'elementary-number-theory-reference',shortDescription:'Divisibility, modular arithmetic, groups modulo n, primes, congruences, and primality testing.',description:'The elementary arithmetic reference track: divisibility, modular arithmetic, CRT, multiplicative groups modulo n, Euler’s totient, primes, primality testing, polynomial congruences, and pseudoprime constructions.',startLabel:'Open the number-theory reference',group:'Mathematical Foundations'},
	{name:'Abstract Algebra Foundations',slug:'abstract-algebra-foundations',shortDescription:'Groups, homomorphisms, rings, ideals, fields, extensions, and polynomial rings.',description:'A pure-algebra path from groups and quotient structures through rings and ideals, field extensions, polynomial rings, modules, and the first bridge to algebraic geometry.',startLabel:'Start with groups',group:'Mathematical Foundations'},
	{name:'Finite Fields & Polynomial Arithmetic',slug:'finite-fields-polynomial-arithmetic',shortDescription:'Prime fields, extension fields, irreducible polynomials, Frobenius maps, and finite-field factorization.',description:'A computational algebra path through finite fields and polynomial arithmetic: constructing F_{p^n}, polynomial bases, inverses, Frobenius/trace/norm, irreducibility, roots, and factorization over finite fields.',startLabel:'Start with finite fields',group:'Mathematical Foundations'},
	{name:'Computational Number Theory',slug:'computational-number-theory',shortDescription:'Arithmetic functions, primes, Gaussian integers, characters, Gauss/Jacobi sums, and quadratic forms.',description:'A computational pure-number-theory path covering multiplicative arithmetic functions, prime distribution experiments, Gaussian integers, Dirichlet characters, Gauss/Jacobi sums, binary quadratic forms, and norm equations.',startLabel:'Start with arithmetic functions',group:'Mathematical Foundations'},
	{name:'Linear Algebra Foundations',slug:'linear-algebra-foundations',shortDescription:'Vectors, matrices, linear maps, orthogonality, Gram–Schmidt, determinants, and volume.',description:'The pure linear-algebra prerequisite path used throughout the mathematical side of CryptoCave: vector spaces, bases, linear maps, orthogonal projections, Gram–Schmidt, determinants, and volume.',startLabel:'Start with vectors and matrices',group:'Mathematical Foundations'},
	{name:'Lattices & Lattice-Based Cryptography',slug:'lattices-lattice-based-cryptography',shortDescription:'Lattice geometry, exact 2D reduction, hard problems, SIS/LWE, structured rings, NTRU, toy LLL attacks, PQC standards, and cryptanalysis.',description:'A complete lattice path from discrete geometry and exact 2D Gaussian reduction through q-ary lattices, SIS and LWE, structured Ring/Module-LWE, NTRU, a worked toy NTRU/LLL recovery, modern lattice-based post-quantum standards, and the main cryptanalytic uses of lattice reduction.',startLabel:'Start with lattice geometry',group:'Mathematical Foundations'},
	{name:'Symmetric Cryptography',slug:'symmetric-cryptography',shortDescription:'SPNs, DES, AES, modes, AEAD, and linear cryptanalysis.',description:'A construction-and-analysis path through block-cipher structure, DES, AES, padding/modes, authenticated encryption and AEAD, and Matsui-style linear cryptanalysis.',startLabel:'Start with SPNs',group:'Core Cryptography'},
	{name:'Hash Functions & MACs',slug:'hash-functions-macs',shortDescription:'Hash security, birthday bounds, SHA-2, length extension, SHA-3, MACs, and algebraic hashes.',description:'A complete hash-and-authentication path from core resistance properties through generic attacks, Merkle–Damgård/SHA-256, length extension, sponge/Keccak/SHA-3, HMAC/KMAC, and proof-oriented algebraic hashes.',startLabel:'Start with the hash primer',group:'Core Cryptography'},
	{name:'Randomness & Stream Ciphers',slug:'randomness-stream-ciphers',shortDescription:'PRGs, LCGs, LFSRs, correlation attacks, RC4, ChaCha20, and Dual_EC_DRBG.',description:'A construction-and-cryptanalysis path from pseudorandomness and stream-cipher security through predictable linear generators, LFSR correlation attacks, historical RC4 failures, modern ChaCha20, and the Dual_EC_DRBG standards lesson.',startLabel:'Start with pseudorandom generators',group:'Core Cryptography'},
	{name:'Discrete Logarithm Algorithms',slug:'discrete-logarithm-algorithms',shortDescription:'DLP/ECDLP foundations followed by BSGS, Pohlig–Hellman, and Pollard’s rho.',description:'A focused algorithmic path through discrete logarithms: group formulation, elliptic-curve variants, generic square-root algorithms, smooth-order reductions, and Pollard-style collision search.',startLabel:'Start with the DLP',group:'Public-Key & Algebraic Systems'},
	{name:'Diffie–Hellman & ElGamal',slug:'diffie-hellman-elgamal',shortDescription:'Key exchange, safe-prime groups, failure modes, and ElGamal encryption.',description:'A protocol-oriented path around discrete-logarithm systems: Diffie–Hellman, safe-prime subgroup structure, active and parameter-validation failures, and ElGamal.',startLabel:'Start with Diffie–Hellman',group:'Public-Key & Algebraic Systems'},
	{name:'Elliptic Curve Mathematics',slug:'elliptic-curve-mathematics',shortDescription:'Plane cubics, rational points, curve models, torsion, Frobenius, pairings, point counting, and isogenies.',description:'The pure mathematical elliptic-curve path: geometry of nonsingular cubics, the group law, rational points and Mordell–Weil structure, torsion, finite-field arithmetic, alternate models, division polynomials, pairings, Schoof point counting, and isogenies.',startLabel:'Start with plane cubics',group:'Mathematical Foundations'},
	{name:'Elliptic Curve Cryptanalysis',slug:'elliptic-curve-cryptanalysis',shortDescription:'Structural weaknesses and reductions that make particular elliptic-curve discrete logarithms easier.',description:'A focused security-analysis path separating curve mathematics from attacks: singular-curve reductions, MOV pairing reductions, and Smart’s attack on anomalous curves.',startLabel:'Start with singular curves',group:'Security Analysis'},
	{name:'Digital Signatures',slug:'digital-signatures',shortDescription:'Signature security models, RSA/PSS, DSA, ECDSA, Schnorr, EdDSA, and nonce/validation failures.',description:'A modernized signature path from the unforgeability model and hash-then-sign discipline through RSA/PSS, historical ElGamal/DSA, ECDSA and nonce failures, Schnorr, and EdDSA.',startLabel:'Start with signature security',group:'Public-Key & Algebraic Systems'},
	{name:'Secret Sharing & Polynomial Tools',slug:'secret-sharing-polynomial-tools',shortDescription:'Additive/Shamir sharing, share arithmetic, interpolation, ramp/proactive variants, packed sharing, NTTs, and robust reconstruction.',description:'The mathematical foundation for distributed cryptography: additive and Shamir sharing, arithmetic and degree growth, interpolation, ramp/proactive/access-structure extensions, packed sharing, roots of unity and NTT engineering, and robust Reed–Solomon/Gao reconstruction.',startLabel:'Start with additive sharing',group:'Distributed Cryptography'},
	{name:'Secure Multiparty Computation',slug:'secure-multiparty-computation',shortDescription:'Arithmetic-circuit MPC, Beaver triples, authenticated shares, SPDZ, malicious-security boundaries, and private-ML engineering.',description:'A protocol-engineering path from secret-shared arithmetic to secure multiplication, offline/online preprocessing, SPDZ authenticated shares and MAC checks, malicious-security boundaries, vectorized computation, fixed-point arithmetic, and private-machine-learning case studies.',startLabel:'Start from secret sharing to MPC',group:'Privacy-Preserving Computation'},
	{name:'Threshold Cryptography Engineering',slug:'threshold-cryptography-engineering',shortDescription:'VSS, DKG, distributed Schnorr debugging, threshold ECDSA/TinySig, FROST, validation, and distributed randomness.',description:'A protocol-engineering path from verifiable sharing through complaints and qualification, multi-dealer DKG, threshold-signature algebra, a real distributed Schnorr/BIP340 debugging case study, the nonlinear threshold-ECDSA problem and TinySig preprocessing prototype, threshold Schnorr/FROST, a line-by-line SageMath proof-of-concept audit, RFC 9591 boundaries, advanced DKG/PVSS notes, and distributed randomness.',startLabel:'Start with VSS',group:'Distributed Cryptography'},
	{name:'Oblivious Transfer',slug:'oblivious-transfer',shortDescription:'Rabin OT, 1-out-of-2 transfer, and the route from base OT to modern OT extension.',description:'A focused MPC foundation path: probabilistic Rabin OT, deterministic 1-out-of-2 OT from trapdoor permutations, security-model caveats, and the progression to Naor–Pinkas-style selection protocols and OT extension.',startLabel:'Start with Rabin OT',group:'Privacy-Preserving Computation'},
	{name:'Homomorphic Encryption',slug:'homomorphic-encryption',shortDescription:'PHE constructions, Paillier-family systems, SHE/FHE, DGHV, BGV, and BFV.',description:'A progressive homomorphic-encryption path from classical partially homomorphic schemes through Paillier-family constructions, bounded/noisy computation, integer FHE, and modern RLWE-based BGV/BFV techniques.',startLabel:'Start with HE foundations',group:'Privacy-Preserving Computation'},
	{name:'Zero-Knowledge Proof Systems',slug:'zero-knowledge-proof-systems',shortDescription:'Foundations, Sigma protocols, Fiat–Shamir, arithmetization, polynomial commitments, SNARKs, STARKs, FRI, and recursion.',description:'A complete proof-systems path from simulation-based zero knowledge and special soundness through arithmetic circuits, R1CS/QAP arithmetization, KZG/IPA polynomial commitments, Groth16, PLONK, transparent STARK/FRI systems, recursive composition, and proof-system tradeoffs.',startLabel:'Start with zero-knowledge foundations',group:'Privacy-Preserving Computation'},
	{name:'RSA Deep Dives',slug:'rsa-deep-dives',shortDescription:'A structured RSA cryptanalysis sequence from textbook failures through ROCA and structured-factorization methods.',description:'A deliberately ordered RSA cryptanalysis block: textbook RSA, common modulus, broadcast, Wiener, Coppersmith/LLL, Boneh–Durfee, partial key exposure, related messages, padding oracles, Manger, ROCA, factorization-friendly prime structure, and synthesis.',startLabel:'Start Deep Dive I',group:'Security Analysis'},
];

export function getSeriesByName(name: string): SeriesDefinition | undefined { return SERIES.find((series) => series.name === name); }
export function getSeriesBySlug(slug: string): SeriesDefinition | undefined { return SERIES.find((series) => series.slug === slug); }
