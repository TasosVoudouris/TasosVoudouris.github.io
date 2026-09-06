export const TOPIC_NAMES = [
	'Mathematical Foundations',
	'Number Theory',
	'Symmetric Cryptography',
	'Public-Key Cryptography',
	'Zero-Knowledge Proofs',
	'MPC',
	'Threshold Cryptography',
	'Post-Quantum Cryptography',
	'Formal Verification',
	'Implementations',
] as const;

export type TopicName = (typeof TOPIC_NAMES)[number];

export type TopicDefinition = {
	name: TopicName;
	slug: string;
	description: string;
};

export const TOPICS: readonly TopicDefinition[] = [
	{
		name: 'Mathematical Foundations',
		slug: 'mathematical-foundations',
		description:
			'Groups, rings, fields, algebraic structures, and the mathematics underlying cryptography.',
	},
	{
		name: 'Number Theory',
		slug: 'number-theory',
		description:
			'Prime numbers, modular arithmetic, discrete logarithms, and computational number theory.',
	},
	{
		name: 'Symmetric Cryptography',
		slug: 'symmetric-cryptography',
		description:
			'Block ciphers, stream ciphers, authenticated encryption, hashing, and symmetric primitives.',
	},
	{
		name: 'Public-Key Cryptography',
		slug: 'public-key-cryptography',
		description:
			'RSA, Diffie–Hellman, elliptic curves, signatures, encryption, and public-key infrastructure.',
	},
	{
		name: 'Zero-Knowledge Proofs',
		slug: 'zero-knowledge-proofs',
		description:
			'SNARKs, STARKs, polynomial commitments, arithmetization, recursion, and modern proof systems.',
	},
	{
		name: 'MPC',
		slug: 'mpc',
		description:
			'Secure multiparty computation, secret sharing, distributed protocols, and private computation.',
	},
	{
		name: 'Threshold Cryptography',
		slug: 'threshold-cryptography',
		description:
			'Threshold signatures, distributed key generation, threshold encryption, and distributed trust.',
	},
	{
		name: 'Post-Quantum Cryptography',
		slug: 'post-quantum-cryptography',
		description:
			'Lattice-based, hash-based, code-based, and other quantum-resistant cryptographic systems.',
	},
	{
		name: 'Formal Verification',
		slug: 'formal-verification',
		description:
			'Formal models, symbolic analysis, protocol verification, and machine-assisted security reasoning.',
	},
	{
		name: 'Implementations',
		slug: 'implementations',
		description:
			'Code, experiments, benchmarks, implementation notes, and reproducible cryptographic engineering.',
	},
];

export function getTopicByName(name: string): TopicDefinition | undefined {
	return TOPICS.find((topic) => topic.name === name);
}

export function getTopicBySlug(slug: string): TopicDefinition | undefined {
	return TOPICS.find((topic) => topic.slug === slug);
}