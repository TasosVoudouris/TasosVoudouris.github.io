export const TOPIC_NAMES = [
	'Cryptography Fundamentals',
	'Classical Cryptography',
	'Mathematical Foundations',
	'Abstract Algebra',
	'Finite Fields',
	'Linear Algebra',
	'Lattice Theory',
	'Algebraic Geometry',
	'Elliptic Curve Theory',
	'Number Theory',
	'Discrete Logarithms',
	'Public-Key Cryptography',
	'Digital Signatures',
	'Key Exchange',
	'Elliptic-Curve Cryptography',
	'Symmetric Cryptography',
	'Hash Functions',
	'Cryptanalysis',
	'Implementation Security',
	'Lattice Methods',
	'Cryptographic Engineering',
	'Randomness & Entropy',
	'Zero-Knowledge Proofs',
	'Polynomial Commitments',
	'MPC',
	'Secret Sharing',
	'Threshold Cryptography',
	'Homomorphic Encryption',
	'Post-Quantum Cryptography',
	'Formal Verification',
] as const;

export type TopicName = (typeof TOPIC_NAMES)[number];

export type TopicGroup =
	| 'Foundations'
	| 'Core Cryptography'
	| 'Security Analysis'
	| 'Engineering & Assurance'
	| 'Modern Cryptography';

export type TopicDefinition = {
	name: TopicName;
	slug: string;
	description: string;
	group: TopicGroup;
};

export const TOPIC_GROUPS: readonly TopicGroup[] = [
	'Foundations',
	'Core Cryptography',
	'Security Analysis',
	'Engineering & Assurance',
	'Modern Cryptography',
];

export const TOPICS: readonly TopicDefinition[] = [
	{
		name: 'Cryptography Fundamentals',
		slug: 'cryptography-fundamentals',
		description: 'Security goals, cryptographic vocabulary, bit operations, encodings, and the practical language needed before studying constructions.',
		group: 'Foundations',
	},
	{
		name: 'Classical Cryptography',
		slug: 'classical-cryptography',
		description: 'Historical ciphers and the classical cryptanalytic techniques that motivated modern security models.',
		group: 'Foundations',
	},
	{
		name: 'Mathematical Foundations',
		slug: 'mathematical-foundations',
		description: 'Groups, rings, fields, algebraic structure, and the mathematical language used throughout cryptography.',
		group: 'Foundations',
	},
	{
		name: 'Abstract Algebra',
		slug: 'abstract-algebra',
		description: 'Groups, rings, ideals, fields, modules, homomorphisms, quotient structures, and algebraic extensions.',
		group: 'Foundations',
	},
	{
		name: 'Finite Fields',
		slug: 'finite-fields',
		description: 'Finite-field construction, extension fields, polynomial bases, Frobenius maps, irreducibility, and finite-field algorithms.',
		group: 'Foundations',
	},
	{
		name: 'Linear Algebra',
		slug: 'linear-algebra',
		description: 'Vectors, matrices, linear maps, vector spaces, bases, determinants, orthogonality, and computational linear algebra.',
		group: 'Foundations',
	},
	{
		name: 'Lattice Theory',
		slug: 'lattice-theory',
		description: 'Integer lattices, bases, Gram–Schmidt orthogonalization, determinants, fundamental regions, and lattice reduction.',
		group: 'Foundations',
	},
	{
		name: 'Algebraic Geometry',
		slug: 'algebraic-geometry',
		description: 'Affine and projective algebraic sets, polynomial ideals, coordinate rings, plane curves, and the geometric language behind elliptic curves.',
		group: 'Foundations',
	},
	{
		name: 'Elliptic Curve Theory',
		slug: 'elliptic-curve-theory',
		description: 'The pure mathematics of elliptic curves: plane cubics, rational points, torsion, heights, Frobenius, division polynomials, pairings, and isogenies.',
		group: 'Foundations',
	},
	{
		name: 'Number Theory',
		slug: 'number-theory',
		description: 'Divisibility, modular arithmetic, primes, continued fractions, CRT, polynomial congruences, and computational number theory.',
		group: 'Foundations',
	},
	{
		name: 'Discrete Logarithms',
		slug: 'discrete-logarithms',
		description: 'DLP/ECDLP structure, generic algorithms, smooth-order reductions, and the hardness assumptions behind many public-key systems.',
		group: 'Foundations',
	},
	{
		name: 'Public-Key Cryptography',
		slug: 'public-key-cryptography',
		description: 'RSA, Diffie–Hellman, ElGamal, Paillier, elliptic curves, encryption, signatures, key exchange, and public-key constructions.',
		group: 'Core Cryptography',
	},
	{
		name: 'Digital Signatures',
		slug: 'digital-signatures',
		description: 'RSA/PSS, DSA, ECDSA, Schnorr, EdDSA, signature security models, nonce failures, encodings, and verification engineering.',
		group: 'Core Cryptography',
	},
	{
		name: 'Key Exchange',
		slug: 'key-exchange',
		description: 'Diffie–Hellman-style key agreement, parameter selection, authentication requirements, and deployment security.',
		group: 'Core Cryptography',
	},
	{
		name: 'Elliptic-Curve Cryptography',
		slug: 'elliptic-curve-cryptography',
		description: 'Elliptic-curve groups, finite-field arithmetic, curve models, pairings, point counting, ECDLP techniques, and isogenies.',
		group: 'Core Cryptography',
	},
	{
		name: 'Symmetric Cryptography',
		slug: 'symmetric-cryptography',
		description: 'Block ciphers, modes of operation, authenticated encryption, and symmetric-key constructions.',
		group: 'Core Cryptography',
	},
	{
		name: 'Hash Functions',
		slug: 'hash-functions',
		description: 'Cryptographic hashing, preimage and collision resistance, digest construction, and implementation practice.',
		group: 'Core Cryptography',
	},
	{
		name: 'Cryptanalysis',
		slug: 'cryptanalysis',
		description: 'Failure modes, attacks, security assumptions, algebraic weaknesses, oracle techniques, and cryptanalytic reasoning.',
		group: 'Security Analysis',
	},
	{
		name: 'Implementation Security',
		slug: 'implementation-security',
		description: 'Side channels, faults, validation failures, error oracles, key-generation defects, and implementation-level security.',
		group: 'Security Analysis',
	},
	{
		name: 'Lattice Methods',
		slug: 'lattice-methods',
		description: 'LLL, small-root techniques, Coppersmith-style reasoning, lattice reduction, and lattice-based cryptographic mathematics.',
		group: 'Security Analysis',
	},
	{
		name: 'Cryptographic Engineering',
		slug: 'cryptographic-engineering',
		description: 'Executable implementations, experiments, testing, performance, and the engineering details behind cryptographic code.',
		group: 'Engineering & Assurance',
	},
	{
		name: 'Randomness & Entropy',
		slug: 'randomness-entropy',
		description: 'Entropy, CSPRNGs, operating-system randomness, distributed randomness beacons, bias resistance, and public verifiability.',
		group: 'Engineering & Assurance',
	},
	{
		name: 'Formal Verification',
		slug: 'formal-verification',
		description: 'Formal models, symbolic analysis, protocol verification, and machine-assisted security reasoning.',
		group: 'Engineering & Assurance',
	},
	{
		name: 'Zero-Knowledge Proofs',
		slug: 'zero-knowledge-proofs',
		description: 'SNARKs, STARKs, polynomial commitments, arithmetization, recursion, and modern proof systems.',
		group: 'Modern Cryptography',
	},
	{
		name: 'Polynomial Commitments',
		slug: 'polynomial-commitments',
		description: 'Commitment schemes for polynomials, including KZG, inner-product-based constructions, opening proofs, batching, and low-degree commitment interfaces used by modern proof systems.',
		group: 'Modern Cryptography',
	},
	{
		name: 'MPC',
		slug: 'mpc',
		description: 'Secure multiparty computation, distributed protocols, and private computation.',
		group: 'Modern Cryptography',
	},
	{
		name: 'Secret Sharing',
		slug: 'secret-sharing',
		description: 'Shamir-style sharing, robust reconstruction, error correction, and the sharing primitives used in distributed cryptography.',
		group: 'Modern Cryptography',
	},
	{
		name: 'Threshold Cryptography',
		slug: 'threshold-cryptography',
		description: 'Threshold signatures, distributed key generation, threshold encryption, and distributed trust.',
		group: 'Modern Cryptography',
	},
	{
		name: 'Homomorphic Encryption',
		slug: 'homomorphic-encryption',
		description: 'Encryption schemes that support computation on ciphertexts, from additive constructions such as Paillier to more advanced HE systems.',
		group: 'Modern Cryptography',
	},
	{
		name: 'Post-Quantum Cryptography',
		slug: 'post-quantum-cryptography',
		description: 'Lattice-based, hash-based, code-based, isogeny-related, and other quantum-resistant cryptographic research directions.',
		group: 'Modern Cryptography',
	},
];

export function getTopicByName(name: string): TopicDefinition | undefined {
	return TOPICS.find((topic) => topic.name === name);
}

export function getTopicBySlug(slug: string): TopicDefinition | undefined {
	return TOPICS.find((topic) => topic.slug === slug);
}
