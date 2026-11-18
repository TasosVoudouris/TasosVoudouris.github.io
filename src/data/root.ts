// "Root of Trust": long-form research series on post-quantum PKI.
// Published parts live in src/content/root/. The roadmap below lists every
// planned part; a part shows as "published" once an article with the same
// `part` number exists.

export const ROOT_TITLE = 'Root of Trust';
export const ROOT_TAGLINE = 'post-quantum PKI, from the leaf to the root';
export const ROOT_DESCRIPTION =
	'A long-form series on how the web decides whom to trust, why post-quantum signatures break the current design, and how Merkle Tree Certificates fix it. Built from the bytes up, with hand-drawn figures and runnable code.';

export type RoadmapPart = { part: number; title: string; about: string };

export const ROOT_ROADMAP: readonly RoadmapPart[] = [
	{ part: 0, title: 'Who do you trust?', about: 'Signatures, certificates, chains, and the root of trust that nothing proves.' },
	{ part: 1, title: 'A certificate, byte by byte', about: 'ASN.1, DER and X.509 read with a hex editor, field by field.' },
	{ part: 2, title: 'The handshake bill', about: 'Where certificates travel in TLS 1.3 and what every byte costs.' },
	{ part: 3, title: 'When authorities lie', about: 'Mis-issuance, Certificate Transparency, and why logs exist.' },
	{ part: 4, title: 'Merkle trees from zero', about: 'Hashes, roots, inclusion proofs and consistency proofs, by hand.' },
	{ part: 5, title: 'Notes, checkpoints, witnesses', about: 'How a log signs what it saw, and who checks that it never forks.' },
	{ part: 6, title: 'The quantum bill', about: 'ML-DSA and friends: why post-quantum signatures do not fit the old design.' },
	{ part: 7, title: 'Merkle Tree Certificates', about: 'Replacing per-certificate signatures with inclusion proofs.' },
	{ part: 8, title: 'Subtrees and landmarks', about: 'The clever parts of MTC: valid subtrees, covering, landmark-relative certificates.' },
	{ part: 9, title: 'Tiled logs', about: 'Serving a transparency log as static files that anyone can cache.' },
	{ part: 10, title: 'A log that never forks', about: 'Commit order, crashes, and recovering without changing history.' },
	{ part: 11, title: 'Verifying an MTC', about: 'What a browser checks, step by step, and where it can go wrong.' },
];

export const partLabel = (n: number) => String(n).padStart(2, '0');
