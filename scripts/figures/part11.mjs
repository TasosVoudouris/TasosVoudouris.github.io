// Figures for Root of Trust, part 11: "From toy to QCERT"
import { Plate, INK, RED, BLUE, GREEN, PENCIL } from './sketch.mjs';

const AMBER = '#b8741a';
const PAPER2 = '#fbf8ef';

export function part11() {
	// ---------------------------------------------------------------- 1. the map
	const mp = new Plate(1000, 640, {
		seed: 121,
		title: 'Eleven experiments, six modules',
		desc: 'Left, the Python experiments: der.py and 01 (DER), 04 (Merkle trees), 05 (notes and checkpoints), 07 (MTC encodings and verification), 08 (subtree consistency, landmarks), 09 (tiles), 10 (commit protocols). Right, the Rust modules they become: der, merkle, note, mtc, subtree, tiles. Parts 00, 02, 03 and 06 explain the problem and have no module; Part 10 becomes a design rule for the log writer rather than a module.',
	});
	const left = [
		['der.py, 01', 'DER, certificates'],
		['04_merkle.py', 'RFC 9162 trees, proofs'],
		['05_witness.py', 'notes, checkpoints'],
		['07_mtc.py', 'MTC entries, proofs, verify'],
		['08_landmarks.py', 'subtree consistency, landmarks'],
		['09_tiles.py', 'tlog-tiles'],
		['10_never_fork.py', 'commit order'],
	];
	const right = [['der', 0], ['merkle', 1], ['note', 2], ['mtc', 3], ['subtree', 4], ['tiles', 5]];
	mp.text(60, 50, 'Python reference', { size: 21, weight: 700 });
	mp.text(700, 50, 'Rust crate rot-mtc', { size: 21, weight: 700, color: AMBER });
	left.forEach(([f, d], i) => {
		const y = 70 + i * 74;
		mp.rect(60, y, 340, 58, { stroke: INK, fill: PAPER2, fillStyle: 'solid', strokeWidth: 1.5 });
		mp.text(76, y + 26, f, { size: 18, weight: 700 });
		mp.text(76, y + 48, d, { size: 15, color: PENCIL });
	});
	right.forEach(([m], i) => {
		const y = 70 + i * 74;
		mp.rect(700, y, 240, 58, { stroke: AMBER, fill: PAPER2, fillStyle: 'solid', strokeWidth: 2 });
		mp.text(820, y + 36, `${m}.rs`, { anchor: 'middle', size: 20, weight: 700, color: AMBER });
	});
	const link = (li, ri, c = PENCIL) => mp.arrow(404, 70 + li * 74 + 29, 696, 70 + ri * 74 + 29, { stroke: c, strokeWidth: 1.4 });
	link(0, 0); link(1, 1); link(2, 2); link(3, 3); link(3, 4); link(4, 4); link(5, 5);
	mp.arrow(404, 70 + 6 * 74 + 29, 696, 70 + 6 * 74 + 29, { stroke: BLUE, strokeWidth: 1.4 });
	mp.text(700, 70 + 6 * 74 + 36, 'a rule for the log writer:', { size: 17, color: BLUE, weight: 700 });
	mp.text(700, 70 + 6 * 74 + 58, 'stage, lock, then publish', { size: 16, color: BLUE });
	mp.text(60, 625, 'Parts 00, 02, 03 and 06 explain the problem; they measure, they do not become code.', { size: 18, color: PENCIL });

	// ---------------------------------------------------------------- 2. the pipeline
	const pl = new Plate(1000, 460, {
		seed: 122,
		title: 'One set of bytes, two languages',
		desc: 'The Python experiments compute everything. 11_vectors.py freezes the results into one JSON file of test vectors, about 349 KB, with no randomized signatures, so it is identical on every run. The Rust crate rot-mtc reads the same file in cargo test. The draft Appendix C hashes are recomputed on both sides. Later implementations read the same file.',
	});
	const B = (x, y, w, t, s, c) => {
		pl.rect(x, y, w, 110, { stroke: c, fill: PAPER2, fillStyle: 'solid', strokeWidth: 2 });
		pl.text(x + w / 2, y + 42, t, { anchor: 'middle', size: 21, weight: 700, color: c });
		pl.text(x + w / 2, y + 72, s, { anchor: 'middle', size: 15, color: PENCIL });
	};
	B(30, 80, 250, 'Python, Parts 04 to 09', 'the reference: slow, clear', INK);
	B(360, 80, 280, 'root-of-trust-vectors.json', 'deterministic, ~349 KB', GREEN);
	B(720, 80, 250, 'Rust: cargo test', '8 tests, all vectors', AMBER);
	pl.arrow(282, 135, 356, 135, { stroke: INK, strokeWidth: 1.8 });
	pl.text(319, 120, 'freeze', { anchor: 'middle', size: 15, color: PENCIL });
	pl.arrow(642, 135, 716, 135, { stroke: GREEN, strokeWidth: 1.8 });
	pl.text(679, 120, 'check', { anchor: 'middle', size: 15, color: PENCIL });
	pl.rect(360, 260, 280, 80, { stroke: BLUE, fill: 'rgba(40,80,150,0.08)', fillStyle: 'solid', strokeWidth: 1.6 });
	pl.text(500, 294, 'draft -07, Appendix C', { anchor: 'middle', size: 19, weight: 700, color: BLUE });
	pl.text(500, 320, 'recomputed on both sides', { anchor: 'middle', size: 15, color: BLUE });
	pl.arrow(450, 256, 420, 194, { stroke: BLUE, strokeWidth: 1.4 });
	pl.arrow(560, 256, 790, 194, { stroke: BLUE, strokeWidth: 1.4 });
	pl.text(30, 420, 'disagreement anywhere is a bug in one of them, found before any network is involved.', { size: 19, weight: 700 });

	// ---------------------------------------------------------------- 3. landmark-relative verification in Rust
	const lr = new Plate(1000, 620, {
		seed: 123,
		title: 'Verifying a landmark-relative certificate in Rust',
		desc: 'The steps of verify_landmark_relative: split the certificate DER into TBSCertificate, algorithm and signatureValue; check both algorithm fields are id-alg-mtcProof; split the serial into log number and index; parse the MTCProof strictly; rebuild the MTCLogEntry from the TBSCertificate, replacing the public key by its algorithm and SHA-256; hash it as a leaf; evaluate the inclusion proof; compare with the trusted landmark subtree hash. The rebuilt entry matches the Python bytes exactly.',
	});
	const steps = [
		['split the DER', 'TBS, algorithm, signatureValue', INK],
		['check algorithms', 'id-alg-mtcProof, twice', INK],
		['split the serial', 'log 1, index 1005', INK],
		['parse the MTCProof', '[0, 1024), 10 hashes, 0 signatures', AMBER],
		['rebuild the log entry', 'no serial; key -> algorithm + SHA-256', GREEN],
		['leaf hash, evaluate', 'RFC 9162, returning the root', GREEN],
		['compare', 'the trusted landmark hash', BLUE],
	];
	steps.forEach(([t, s, c], i) => {
		const y = 60 + i * 74;
		lr.rect(200, y, 600, 58, { stroke: c, fill: PAPER2, fillStyle: 'solid', strokeWidth: 1.8 });
		lr.text(220, y + 37, `${i + 1}. ${t}`, { size: 20, weight: 700, color: c });
		lr.text(780, y + 37, s, { anchor: 'end', size: 16, color: PENCIL });
		if (i) lr.arrow(500, y - 14, 500, y - 2, { stroke: PENCIL, strokeWidth: 1.2 });
	});
	lr.text(820, 60 + 4 * 74 + 37, 'same bytes as Python', { size: 16, color: GREEN, weight: 700 });
	lr.text(200, 600, 'no signature verified; one SHA-256 chain from the certificate to a hash the browser holds.', { size: 18, weight: 700 });

	// ---------------------------------------------------------------- 4. the vector file
	const vf = new Plate(1000, 480, {
		seed: 124,
		title: 'What the vector file holds',
		desc: 'Counts per section: 21 tree hashes, 210 inclusion proofs, 210 consistency proofs, 567 subtree consistency proofs, 10 covering cases, 11 validity cases, 15 tile paths (8 of them invalid), 6 layouts, 2 node mappings, 4 Appendix C hashes, 5 relative OIDs, 2 cosigned messages, 1 MTCProof, 1 landmark-relative certificate, 1 checkpoint body, 1 key ID.',
	});
	const rows = [
		['Merkle: inclusion + consistency', 420, INK],
		['subtree consistency proofs', 567, GREEN],
		['subtree validity + covering', 21, GREEN],
		['tile paths, layouts, nodes', 23, BLUE],
		['MTC encodings, a certificate', 10, AMBER],
		['draft Appendix C hashes', 4, BLUE],
	];
	const VX = 400, VW = 500;
	rows.forEach(([l, n, c], i) => {
		const y = 50 + i * 62;
		vf.text(VX - 16, y + 34, l, { anchor: 'end', size: 18, weight: 700, color: c });
		const w = Math.max((n / 600) * VW, 6);
		vf.rect(VX, y + 10, w, 36, { stroke: c, fill: c, fillStyle: 'hachure', hachureGap: 6, strokeWidth: 1.3 });
		vf.text(VX + w + 12, y + 36, String(n), { size: 18, weight: 700, color: c });
	});
	vf.text(30, 440, 'the four Appendix C hashes each stand for thousands of proofs: one line per case, one running SHA-256.', { size: 17, color: PENCIL });

	// ---------------------------------------------------------------- 5. what is left
	const rm = new Plate(1000, 560, {
		seed: 125,
		title: 'From the core to a system',
		desc: 'Done in this crate: hashing and parsing, tested against the vectors. Next, in order: signatures through a vetted ML-DSA library; the cosigned subtree and checkpoint protocol with witnesses; the tiled log writer with a lock and staging, following Part 10; landmark allocation and validation, following Part 08; and certificate selection in TLS. Fuzzing for every parser throughout.',
	});
	const items = [
		['done', 'hashing, proofs, tiles, encodings, landmark check', GREEN],
		['next', 'signatures: ML-DSA from a vetted library, never hand-written', AMBER],
		['next', 'cosigners: subtree and checkpoint cosigning, witnesses', AMBER],
		['next', 'the log writer: tiles, lock, staging (Part 10)', AMBER],
		['next', 'landmarks: allocation, validation, distribution (Part 08)', AMBER],
		['later', 'TLS: trust anchor IDs and certificate selection', PENCIL],
		['always', 'fuzz every parser: DER, MTCProof, tile paths, notes', RED],
	];
	items.forEach(([k, t, c], i) => {
		const y = 50 + i * 66;
		rm.rect(40, y, 120, 46, { stroke: c, fill: c, fillStyle: k === 'done' ? 'solid' : 'hachure', hachureGap: 7, strokeWidth: 1.6 });
		rm.text(100, y + 30, k, { anchor: 'middle', size: 18, weight: 700, color: k === 'done' ? PAPER2 : INK });
		rm.text(190, y + 30, t, { size: 19, color: INK });
	});
	rm.text(40, 540, 'each step gets its own vectors before its own code.', { size: 20, weight: 700 });

	return { '11-map': mp, '11-pipeline': pl, '11-verify': lr, '11-vectors': vf, '11-next': rm };
}
