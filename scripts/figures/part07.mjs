// Figures for Root of Trust, part 07: "Merkle Tree Certificates"
import { Plate, INK, RED, BLUE, GREEN, PENCIL } from './sketch.mjs';

const AMBER = '#b8741a';
const PAPER2 = '#fbf8ef';
const fmt = (n) => Math.round(n).toLocaleString('en-US');

export function part07() {
	// ---------------------------------------------------------------- 1. issuance flow
	const fl = new Plate(1000, 640, {
		seed: 81,
		title: 'Log first, certificate second',
		desc: 'The subscriber asks the CA. The CA appends a log entry to its own issuance log, then signs subtrees of the log as a cosigner. Witnesses fetch the same entries, check them, and cosign the subtrees too. Only then does the CA build the certificate: the TBSCertificate, an inclusion proof to a subtree, and the cosignatures. Later, landmark subtrees are pushed to browsers, and certificates relative to them need no signatures.',
	});
	const box = (p, x, y, w, h, title, sub, c) => {
		p.rect(x, y, w, h, { stroke: c, fill: PAPER2, fillStyle: 'solid', strokeWidth: 2 });
		p.text(x + w / 2, y + 36, title, { anchor: 'middle', size: 24, weight: 700, color: c });
		if (sub) p.text(x + w / 2, y + 66, sub, { anchor: 'middle', size: 17, color: PENCIL });
	};
	box(fl, 30, 60, 200, 110, 'subscriber', 'key pair,\nname to prove', INK);
	box(fl, 320, 40, 340, 150, 'CA', '1. validate the request\n2. APPEND entry to its log\n3. sign subtrees (as cosigner)', BLUE);
	box(fl, 760, 40, 210, 150, 'witnesses', 'fetch the entries,\ncheck the subtree,\ncosign it', GREEN);
	box(fl, 320, 290, 340, 140, 'certificate', 'TBSCertificate\n+ inclusion proof to a subtree\n+ cosignatures', INK);
	box(fl, 30, 300, 200, 110, 'server', 'sends it\nin TLS', INK);
	box(fl, 760, 300, 210, 120, 'browser', 'rebuilds the entry,\nchecks proof\nand cosignatures', AMBER);
	fl.arrow(232, 110, 316, 110, { stroke: INK, strokeWidth: 1.8 });
	fl.arrow(662, 90, 756, 90, { stroke: BLUE, strokeWidth: 1.8 });
	fl.text(709, 78, 'subtree', { anchor: 'middle', size: 16, color: BLUE });
	fl.arrow(756, 150, 662, 150, { stroke: GREEN, strokeWidth: 1.8 });
	fl.text(709, 172, 'cosig', { anchor: 'middle', size: 16, color: GREEN });
	fl.arrow(490, 192, 490, 286, { stroke: INK, strokeWidth: 1.8 });
	fl.text(500, 246, '4. only now: build', { size: 18, color: INK, weight: 700 });
	fl.arrow(316, 360, 234, 360, { stroke: INK, strokeWidth: 1.8 });
	fl.curvedArrow(130, 414, 450, 560, 860, 424, { stroke: INK, strokeWidth: 1.6 });
	fl.text(450, 520, 'TLS handshake', { anchor: 'middle', size: 18, color: PENCIL });
	fl.arrow(975, 196, 975, 296, { stroke: AMBER, strokeWidth: 1.6 });
	fl.text(962, 236, 'landmarks,', { size: 15, color: AMBER, anchor: 'end' });
	fl.text(962, 254, 'via updater', { size: 15, color: AMBER, anchor: 'end' });
	fl.text(30, 618, 'CT logs a certificate after it exists; here the log entry exists before the certificate can be built.', { size: 20, weight: 700 });

	// ---------------------------------------------------------------- 2. log entry vs TBSCertificate
	const en = new Plate(1000, 620, {
		seed: 82,
		title: 'What the log entry keeps from the certificate',
		desc: 'Left, the TBSCertificate fields with their sizes in the toy: version 5, serial 9, signature algorithm 12, issuer 22, validity 32, subject 26, subject public key info 1,334 bytes, extensions 51. Right, the TBSCertificateLogEntry: no serial, no signature algorithm, and the 1,334-byte public key replaced by its algorithm identifier and a 32-byte SHA-256 hash. The whole log entry is 187 bytes.',
	});
	const L = [['version', 5, INK], ['serialNumber', 9, RED], ['signature (alg)', 12, RED], ['issuer', 22, INK],
		['validity', 32, INK], ['subject', 26, INK], ['subjectPublicKeyInfo', 1334, BLUE], ['extensions', 51, INK]];
	const R = [['version', 5, INK], ['issuer', 22, INK], ['validity', 32, INK], ['subject', 26, INK],
		['subjectPublicKeyAlgorithm', 13, BLUE], ['subjectPublicKeyInfoHash', 34, BLUE], ['extensions', 51, INK]];
	en.text(40, 52, 'TBSCertificate (in the certificate)', { size: 22, weight: 700 });
	en.text(560, 52, 'TBSCertificateLogEntry (in the log)', { size: 22, weight: 700, color: GREEN });
	const rowH = (n) => (n > 1000 ? 150 : 46);
	let y = 70;
	const ly = {};
	for (const [f, n, c] of L) {
		const h = rowH(n);
		en.rect(40, y, 400, h - 6, { stroke: c, fill: c === RED ? 'rgba(190,40,40,0.08)' : PAPER2, fillStyle: 'solid', strokeWidth: 1.6 });
		en.text(54, y + 28, f, { size: 19, color: c, weight: 700 });
		en.text(426, y + 28, `${fmt(n)} B`, { size: 18, color: PENCIL, anchor: 'end' });
		ly[f] = y + h / 2 - 3;
		y += h;
	}
	en.text(240, ly['subjectPublicKeyInfo'] + 30, 'ML-DSA-44 key: 1,312 bytes', { size: 18, color: BLUE, anchor: 'middle' });
	y = 70;
	const ry = {};
	for (const [f, n, c] of R) {
		en.rect(560, y, 400, 40, { stroke: c, fill: PAPER2, fillStyle: 'solid', strokeWidth: 1.6 });
		en.text(574, y + 28, f, { size: 18, color: c, weight: 700 });
		en.text(946, y + 28, `${fmt(n)} B`, { size: 18, color: PENCIL, anchor: 'end' });
		ry[f] = y + 20;
		y += 46;
	}
	for (const f of ['version', 'issuer', 'validity', 'subject']) en.line(442, ly[f], 556, ry[f], { stroke: PENCIL, strokeWidth: 1 });
	en.line(442, ly['extensions'], 556, ry['extensions'], { stroke: PENCIL, strokeWidth: 1 });
	en.arrow(442, ly['subjectPublicKeyInfo'] - 20, 556, ry['subjectPublicKeyAlgorithm'], { stroke: BLUE, strokeWidth: 1.6 });
	en.arrow(442, ly['subjectPublicKeyInfo'] + 6, 556, ry['subjectPublicKeyInfoHash'], { stroke: BLUE, strokeWidth: 1.6 });
	en.text(500, ly['subjectPublicKeyInfo'] + 44, 'SHA-256', { anchor: 'middle', size: 17, color: BLUE, weight: 700 });
	en.text(330, ly['serialNumber'] + 7, 'not logged', { size: 17, color: RED, anchor: 'end' });
	en.text(330, ly['signature (alg)'] + 7, 'not logged', { size: 17, color: RED, anchor: 'end' });
	en.text(560, 432, 'MTCLogEntry = extensions (2 B) + type (2 B)', { size: 19 });
	en.text(560, 458, '+ the contents above', { size: 19 });
	en.text(560, 500, '187 bytes per certificate in the log', { size: 24, weight: 700, color: GREEN });
	en.text(560, 540, 'the serial is the log position;', { size: 18, color: RED });
	en.text(560, 562, 'the signature is the proof.', { size: 18, color: RED });
	en.text(40, 600, 'leaf hash = SHA-256(0x00 || MTCLogEntry): the browser recomputes it from the certificate it was given.', { size: 19, color: PENCIL });

	// ---------------------------------------------------------------- 3. MTCProof anatomy
	const pr = new Plate(1000, 600, {
		seed: 83,
		title: 'Where the 8,976 bytes go',
		desc: 'A standalone certificate of 8,976 bytes: 4 bytes of outer header, 1,495 bytes of TBSCertificate (1,334 of them the public key), 12 bytes of algorithm identifier, and a 7,465-byte signatureValue holding the MTCProof. The MTCProof is 2 bytes of extensions, 12 bytes of start and end, 162 bytes of inclusion proof (5 hashes), 3 bytes of length, and 7,281 bytes of three cosignatures from the CA and two witnesses. A landmark-relative certificate keeps the TBSCertificate and replaces the 7,465 bytes with 344.',
	});
	const X0 = 40, SCALE = 920 / 8976;
	const segs = [['hdr', 4, INK], ['TBSCertificate', 1495, INK], ['alg', 12, INK], ['signatureValue = MTCProof', 7465, AMBER]];
	let x = X0;
	for (const [l, n, c] of segs) {
		const w = Math.max(n * SCALE, 3);
		pr.rect(x, 80, w, 70, { stroke: c, fill: c, fillStyle: 'hachure', hachureGap: 7, strokeWidth: 1.4 });
		if (n > 1000) pr.text(x + w / 2, 72, `${l}: ${fmt(n)} B`, { anchor: 'middle', size: 19, weight: 700, color: c });
		x += w;
	}
	pr.text(X0 + 1334 * SCALE / 2 + 10, 182, 'public key 1,334', { anchor: 'middle', size: 17, color: BLUE });
	pr.line(X0 + 14 * SCALE, 160, X0 + 1348 * SCALE, 160, { stroke: BLUE, strokeWidth: 2 });
	const mx0 = X0 + 1511 * SCALE;
	const parts = [['ext 2', 2], ['start, end 12', 12], ['proof 162', 162], ['len 3', 3], ['CA cosig 2,427', 2427], ['witness 2,427', 2427], ['witness 2,427', 2427]];
	pr.line(mx0, 152, 40, 260, { stroke: AMBER, strokeWidth: 1 });
	pr.line(X0 + 920, 152, 960, 260, { stroke: AMBER, strokeWidth: 1 });
	const S2 = 920 / 7465;
	x = 40;
	parts.forEach(([l, n], i) => {
		const w = Math.max(n * S2, 4);
		const c = l.includes('cosig') || l.includes('witness') ? (i === 4 ? BLUE : GREEN) : INK;
		pr.rect(x, 270, w, 70, { stroke: c, fill: c, fillStyle: n > 100 ? 'hachure' : 'solid', hachureGap: 7, strokeWidth: 1.4 });
		if (n > 1000) pr.text(x + w / 2, 312, l, { anchor: 'middle', size: 19, weight: 700, color: c });
		x += w;
	});
	pr.text(40, 372, 'ext, start, end, 5 proof hashes, length: 179 bytes', { size: 18, color: INK });
	pr.text(960, 372, 'each cosignature: ID length 1 + ID 4 + length 2 + ML-DSA-44 2,420', { size: 18, color: PENCIL, anchor: 'end' });
	pr.text(40, 440, 'the Merkle part costs 179 bytes. The signatures cost 7,281.', { size: 24, weight: 700 });
	pr.text(40, 490, 'landmark-relative: same TBSCertificate, and an MTCProof of 339 bytes (10 hashes, no signatures).', { size: 20, color: GREEN, weight: 700 });
	pr.text(40, 528, 'total 1,855 bytes, and most of it is the subscriber\'s own public key.', { size: 20, color: GREEN });
	pr.text(40, 580, 'sizes from experiments/root-of-trust/07_mtc.py', { size: 16, color: PENCIL });

	// ---------------------------------------------------------------- 4. standalone vs landmark subtrees
	const lm = new Plate(1000, 600, {
		seed: 84,
		title: 'Two ways to name the subtree',
		desc: 'The log runs from entry 0 to 1,037. A batch of 37 new entries from 1,000 to 1,037 is covered by two subtrees, [992, 1024) and [1024, 1037); the first starts a little before the batch. These are signed right away and give standalone certificates with 5 proof hashes and three cosignatures. Later landmark 1 at size 1,037 is covered by [0, 1024) and [1024, 1037). Entry 1,005 sits in [0, 1024), a 10-hash proof, and the browser already holds that subtree hash, so no signature is needed.',
	});
	const TX0 = 60, TW = 880;
	const tx = (i) => TX0 + (i / 1037) * TW;            // the whole log
	const zx = (i) => TX0 + ((i - 960) / 80) * TW;      // zoom on [960, 1040)
	// whole log, with the landmark subtrees
	lm.text(TX0, 58, 'the whole log, landmark 1 at tree size 1,037', { size: 19, color: PENCIL });
	lm.line(TX0, 100, TX0 + TW, 100, { stroke: INK, strokeWidth: 2 });
	for (const v of [0, 256, 512, 768, 1024]) {
		lm.line(tx(v), 92, tx(v), 108, { stroke: INK });
		lm.text(tx(v), 84, fmt(v), { anchor: 'middle', size: 16, color: PENCIL });
	}
	lm.rect(tx(0), 116, tx(1024) - tx(0), 40, { stroke: GREEN, fill: 'rgba(60,130,70,0.10)', fillStyle: 'solid', strokeWidth: 1.8 });
	lm.rect(tx(1024), 116, tx(1037) - tx(1024), 40, { stroke: GREEN, fill: PAPER2, fillStyle: 'solid', strokeWidth: 1.5 });
	lm.text(tx(512), 144, 'landmark subtree [0, 1024): the browser already holds its hash', { anchor: 'middle', size: 19, color: GREEN, weight: 700 });
	lm.circle(tx(1005), 100, 12, { stroke: RED, fill: RED, fillStyle: 'solid' });
	// zoom guides
	lm.highlight(tx(960), 92, tx(1037) - tx(960), 16, 'rgba(184,116,26,0.30)');
	lm.line(tx(960), 160, TX0, 250, { stroke: PENCIL, strokeWidth: 1 });
	lm.line(tx(1037), 160, zx(1037), 250, { stroke: PENCIL, strokeWidth: 1 });
	// zoomed axis
	lm.line(TX0, 300, TX0 + TW, 300, { stroke: INK, strokeWidth: 2 });
	for (const v of [960, 976, 992, 1000, 1008, 1024, 1037]) {
		lm.line(zx(v), 292, zx(v), 308, { stroke: INK });
		lm.text(zx(v), 330, fmt(v), { anchor: 'middle', size: 16, color: PENCIL });
	}
	lm.highlight(zx(1000), 290, zx(1037) - zx(1000), 20, 'rgba(184,116,26,0.35)');
	lm.text(zx(1018), 278, 'new batch [1000, 1037)', { anchor: 'middle', size: 18, color: AMBER, weight: 700 });
	lm.rect(zx(992), 350, zx(1024) - zx(992), 40, { stroke: BLUE, fill: 'rgba(40,80,150,0.10)', fillStyle: 'solid', strokeWidth: 1.8 });
	lm.rect(zx(1024), 350, zx(1037) - zx(1024), 40, { stroke: BLUE, fill: PAPER2, fillStyle: 'solid', strokeWidth: 1.8 });
	lm.text(zx(1015), 377, '[992, 1024)', { anchor: 'middle', size: 18, color: BLUE, weight: 700 });
	lm.text(zx(1030.5), 377, '[1024, 1037)', { anchor: 'middle', size: 15, color: BLUE, weight: 700 });
	lm.text(zx(990), 368, 'standalone subtrees,', { anchor: 'end', size: 18, color: BLUE, weight: 700 });
	lm.text(zx(990), 390, 'cosigned right away', { anchor: 'end', size: 18, color: BLUE });
	lm.text(zx(990), 422, '(the left one starts before the batch)', { anchor: 'end', size: 16, color: PENCIL });
	lm.circle(zx(1005), 300, 14, { stroke: RED, fill: RED, fillStyle: 'solid' });
	lm.text(zx(1005), 440, 'entry 1,005', { anchor: 'middle', size: 18, color: RED, weight: 700 });
	lm.line(zx(1005), 310, zx(1005), 420, { stroke: RED, strokeWidth: 1.2 });
	lm.text(60, 500, 'standalone: 5 hashes + 3 cosignatures (7,465 B).', { size: 21, color: BLUE, weight: 700 });
	lm.text(60, 532, 'landmark-relative: 10 hashes, 0 signatures (344 B). Bigger subtree, smaller certificate.', { size: 21, color: GREEN, weight: 700 });
	lm.text(60, 576, 'at real scale: about 12 hashes against about 23 (draft §6.5).', { size: 18, color: PENCIL });

	// ---------------------------------------------------------------- 5. the bill
	const bl = new Plate(1000, 560, {
		seed: 85,
		title: 'The handshake bill, with ML-DSA-44 everywhere',
		desc: 'Authentication bytes in the TLS handshake (Certificate message plus CertificateVerify): classic X.509 with two SCTs and an intermediate 15,271; the same with the intermediate left out 11,353; MTC standalone with the CA and two witnesses 11,417; with the CA and one witness 8,990; landmark-relative 4,296.',
	});
	const rows = [
		['X.509 + 2 SCTs + intermediate', 15271, PENCIL],
		['X.509 + 2 SCTs, leaf only', 11353, PENCIL],
		['MTC standalone, CA + 2 witnesses', 11417, BLUE],
		['MTC standalone, CA + 1 witness', 8990, BLUE],
		['MTC landmark-relative', 4296, GREEN],
	];
	const BX0 = 380, BW = 520, BMAX = 16000;
	rows.forEach(([l, n, c], i) => {
		const yy = 60 + i * 78;
		bl.text(BX0 - 14, yy + 34, l, { anchor: 'end', size: 19, weight: 700, color: c === PENCIL ? INK : c });
		bl.rect(BX0, yy + 10, (n / BMAX) * BW, 38, { stroke: c, fill: c, fillStyle: 'hachure', hachureGap: 6, strokeWidth: 1.4 });
		bl.text(BX0 + (n / BMAX) * BW + 10, yy + 36, `${fmt(n)} B`, { size: 19, color: c === PENCIL ? INK : c, weight: 700 });
	});
	bl.line(BX0, 450, BX0 + BW, 450, { stroke: INK, strokeWidth: 1.2 });
	for (const v of [0, 4000, 8000, 12000, 16000]) {
		bl.line(BX0 + (v / BMAX) * BW, 450, BX0 + (v / BMAX) * BW, 458, { stroke: INK });
		bl.text(BX0 + (v / BMAX) * BW, 480, v ? `${v / 1000} KB` : '0', { anchor: 'middle', size: 16, color: PENCIL });
	}
	bl.text(40, 530, 'standalone MTC drops the intermediate, but keeps three signatures. The landmark drops them too.', { size: 20, weight: 700 });

	return { '07-flow': fl, '07-entry': en, '07-proof': pr, '07-landmarks': lm, '07-bill': bl };
}
