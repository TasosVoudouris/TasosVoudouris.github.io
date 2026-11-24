// Figures for Root of Trust, part 06: "The quantum bill"
import { Plate, INK, RED, BLUE, GREEN, PENCIL } from './sketch.mjs';

const AMBER = '#b8741a';
const PAPER2 = '#fbf8ef';
const fmt = (n) => Math.round(n).toLocaleString('en-US');

// Sizes as printed by experiments/root-of-trust/06_quantum_bill.py
const MENU = [
	['Ed25519', 32, 64, 'classical'], ['ECDSA P-256', 65, 71, 'classical'], ['RSA-2048', 270, 256, 'classical'],
	['ML-DSA-44', 1312, 2420, 'fips'], ['ML-DSA-65', 1952, 3309, 'fips'], ['ML-DSA-87', 2592, 4627, 'fips'],
	['Falcon-512', 897, 655, 'draft'], ['Falcon-1024', 1793, 1271, 'draft'],
	['SLH-DSA-128s', 32, 7856, 'fips'], ['SLH-DSA-128f', 32, 17088, 'fips'],
	['MAYO-1', 1420, 454, 'r3'], ['MAYO-2', 4912, 186, 'r3'], ['SNOVA-24-5-4', 1016, 248, 'r3'],
	['UOV-Ip-pkc', 43576, 128, 'r3'], ['UOV-Is', 412160, 96, 'r3'], ['MQOM-L1', 60, 2916, 'r3'],
];
const COLOR = { classical: PENCIL, fips: BLUE, draft: GREEN, r3: AMBER };

export function part06() {
	// ---------------------------------------------------------------- 1. the menu
	const mn = new Plate(1000, 700, {
		seed: 71,
		title: 'Public key against signature, every scheme measured',
		desc: 'Log-log plot of public key size against signature size. Classical schemes sit in the bottom left corner, under 300 bytes each. ML-DSA sits near 1.3 to 2.6 KB keys and 2.4 to 4.6 KB signatures; Falcon is smaller. SLH-DSA has 32-byte keys and 7.8 to 17 KB signatures. UOV has tiny 96 to 128-byte signatures and 43 to 412 KB keys. MAYO and SNOVA sit in between.',
	});
	const X0 = 120, Y0 = 600, W = 820, H = 520;
	const lx = (v) => X0 + ((Math.log10(v) - 1) / (6 - 1)) * W; // 10 B .. 1 MB
	const ly = (v) => Y0 - ((Math.log10(v) - 1) / (4.5 - 1)) * H; // 10 B .. ~30 KB
	mn.line(X0, Y0, X0 + W, Y0, { stroke: INK, strokeWidth: 1.6 });
	mn.line(X0, Y0, X0, Y0 - H, { stroke: INK, strokeWidth: 1.6 });
	for (const [v, l] of [[10, '10'], [100, '100'], [1000, '1 KB'], [10000, '10 KB'], [100000, '100 KB'], [1000000, '1 MB']]) {
		mn.line(lx(v), Y0, lx(v), Y0 + 8, { stroke: INK });
		mn.text(lx(v), Y0 + 32, l, { anchor: 'middle', size: 18, color: PENCIL });
	}
	for (const [v, l] of [[10, '10'], [100, '100'], [1000, '1 KB'], [10000, '10 KB']]) {
		mn.line(X0 - 8, ly(v), X0, ly(v), { stroke: INK });
		mn.text(X0 - 14, ly(v) + 6, l, { anchor: 'end', size: 18, color: PENCIL });
	}
	mn.text(X0 + W, Y0 + 62, 'public key (travels in certificates, or sits in the client)', { anchor: 'end', size: 19, color: PENCIL });
	mn.text(X0 - 90, Y0 - H - 16, 'signature', { size: 19, color: PENCIL });
	const nudge = { 'Ed25519': [-8, 24, 'end'], 'ECDSA P-256': [10, 26, 'start'], 'RSA-2048': [12, 6, 'start'], 'ML-DSA-65': [12, 18, 'start'],
		'ML-DSA-44': [-12, 0, 'end'], 'ML-DSA-87': [12, -6, 'start'], 'Falcon-512': [-12, 6, 'end'], 'Falcon-1024': [12, 6, 'start'],
		'MAYO-1': [-12, 0, 'end'], 'MAYO-2': [12, 6, 'start'], 'SNOVA-24-5-4': [0, 34, 'middle'], 'SLH-DSA-128s': [14, 6, 'start'],
		'SLH-DSA-128f': [14, 6, 'start'], 'UOV-Ip-pkc': [0, -18, 'middle'], 'UOV-Is': [0, -18, 'middle'], 'MQOM-L1': [14, 6, 'start'] };
	for (const [name, pk, sig, st] of MENU) {
		const [dx, dy, anchor] = nudge[name] ?? [12, 6, 'start'];
		mn.circle(lx(pk), ly(sig), 14, { stroke: COLOR[st], fill: COLOR[st], fillStyle: 'solid' });
		mn.text(lx(pk) + dx, ly(sig) + dy, name, { anchor, size: 18, color: COLOR[st], weight: 700 });
	}
	[['classical', PENCIL], ['FIPS', BLUE], ['draft FIPS 206', GREEN], ['NIST round 3', AMBER]].forEach(([l, c], i) => {
		mn.circle(300 + i * 170, 54, 12, { stroke: c, fill: c, fillStyle: 'solid' });
		mn.text(314 + i * 170, 60, l, { size: 19, color: c, weight: 700 });
	});
	mn.highlight(lx(20), ly(300), lx(400) - lx(20), ly(30) - ly(300), 'rgba(110,110,110,0.12)');

	// ---------------------------------------------------------------- 2. roles
	const rl = new Plate(1000, 560, {
		seed: 72,
		title: 'Not all bytes are paid by the same role',
		desc: 'The leaf sends its public key and signs every handshake online. The intermediate CA sends its public key and signs each leaf. The root and the CT logs keep their public keys in the client; only their signatures travel, and they sign offline. So a scheme with a huge public key and a tiny signature costs almost nothing in those two roles.',
	});
	const roles = [
		['leaf', 'public key: SENT', 'signs: every handshake (online)', BLUE, 'small key + small sig\n+ fast signing'],
		['intermediate CA', 'public key: SENT', 'signs: each leaf (offline)', GREEN, 'small key + small sig'],
		['root CA', 'public key: in the client', 'signs: intermediates (rarely)', AMBER, 'small sig only:\nthe key is free'],
		['2 CT logs', 'public keys: in the client', 'sign: each certificate (offline)', AMBER, 'small sig only,\nsigning must keep up'],
	];
	roles.forEach(([name, pk, signs, c, needs], i) => {
		const y = 60 + i * 120;
		rl.rect(40, y, 300, 96, { stroke: c, fill: PAPER2, fillStyle: 'solid', strokeWidth: 2 });
		rl.text(190, y + 40, name, { anchor: 'middle', size: 26, weight: 700, color: c });
		rl.text(190, y + 74, signs, { anchor: 'middle', size: 18, color: PENCIL });
		rl.text(370, y + 40, pk, { size: 21, color: pk.includes('SENT') ? RED : GREEN, weight: 700 });
		rl.text(720, y + 32, needs, { size: 21, color: c });
	});
	rl.text(40, 545, 'a 43 KB UOV key that sits in every browser costs 0 bytes per handshake; its 128-byte signature is what travels.', { size: 20, weight: 700 });

	// ---------------------------------------------------------------- 3. one scheme everywhere
	const un = new Plate(1000, 640, {
		seed: 73,
		title: 'One scheme for every role: the server flight',
		desc: 'Server first flight with the same scheme in every role: ECDSA 2,930 bytes; SNOVA 5,717; Falcon-512 7,515; MAYO-1 7,555; Falcon-1024 12,384; MAYO-2 13,199; ML-DSA-44 17,169; MQOM 17,145; ML-DSA-65 22,916; ML-DSA-87 30,786; SLH-DSA-128s 41,833. Only ECDSA and SNOVA fit the QUIC budget of about 7,200 bytes; Falcon, MAYO fit the TCP window of 14,600.',
	});
	const bars = [
		['ECDSA P-256 (today)', 2930, PENCIL], ['SNOVA-24-5-4', 5717, AMBER], ['Falcon-512', 7515, GREEN], ['MAYO-1', 7555, AMBER],
		['Falcon-1024', 12384, GREEN], ['MAYO-2', 13199, AMBER], ['MQOM-L1-short', 17145, AMBER], ['ML-DSA-44', 17169, BLUE],
		['ML-DSA-65', 22916, BLUE], ['ML-DSA-87', 30786, BLUE], ['SLH-DSA-128s', 41833, BLUE],
	];
	const BX = 250, SCALE = 680 / 32000;
	bars.forEach(([name, n, c], i) => {
		const y = 50 + i * 48;
		const w = Math.min(n, 32000) * SCALE;
		un.text(BX - 12, y + 20, name, { anchor: 'end', size: 19, weight: 700, color: c === PENCIL ? INK : c });
		un.text(BX - 12, y + 40, n > 32000 ? `${fmt(n)} B, off the chart` : `${fmt(n)} B`, { anchor: 'end', size: 16, color: c === PENCIL ? INK : c });
		un.rect(BX, y + 6, w, 30, { stroke: c, fill: c, fillStyle: 'hachure', hachureGap: 6, strokeWidth: 1.4 });
	});
	const vl = (n, label, c) => {
		un.line(BX + n * SCALE, 40, BX + n * SCALE, 590, { stroke: c, strokeWidth: 2, strokeLineDash: [9, 6] });
		un.text(BX + n * SCALE, 618, label, { anchor: 'middle', size: 19, color: c, weight: 700 });
	};
	vl(7200, 'QUIC ~7,200', RED);
	vl(14600, 'TCP 14,600', INK);

	// ---------------------------------------------------------------- 4. mixing
	const mx = new Plate(1000, 600, {
		seed: 74,
		title: 'Mixing schemes by role',
		desc: 'Three bills split by component. ML-DSA-44 everywhere: 15,802 bytes. ML-DSA-44 for the leaf and Falcon-512 for the CA, root and logs: 8,327. SNOVA for leaf and CA and UOV for root and logs: 3,990. The SCTs and the root signature shrink the most when the signer can use a scheme with a tiny signature.',
	});
	const parts = ['leaf key', 'CertVerify', 'leaf cert sig', '2 SCTs', 'inter key', 'inter cert sig', 'structure'];
	const pcol = [BLUE, RED, GREEN, AMBER, BLUE, GREEN, PENCIL];
	const bills = [
		['ML-DSA-44 everywhere', [1312, 2420, 2420, 4840, 1312, 2420, 1078]],
		['ML-DSA-44 leaf, Falcon-512 elsewhere', [1312, 2420, 655, 1310, 897, 655, 1078]],
		['SNOVA leaf + CA, UOV root + logs', [1016, 248, 248, 256, 1016, 128, 1078]],
	];
	const MX0 = 40, MS = 900 / 16000;
	bills.forEach(([name, vals], i) => {
		const y = 70 + i * 140;
		const total = vals.reduce((a, b) => a + b, 0);
		mx.text(MX0, y, `${name}:  ${fmt(total)} B`, { size: 23, weight: 700 });
		let x = MX0;
		vals.forEach((v, j) => {
			mx.rect(x, y + 14, v * MS, 50, { stroke: pcol[j], fill: pcol[j], fillStyle: j % 2 ? 'hachure' : 'cross-hatch', hachureGap: 7, strokeWidth: 1.3 });
			if (v * MS > 60) mx.text(x + (v * MS) / 2, y + 92, `${fmt(v)}`, { anchor: 'middle', size: 16, color: pcol[j] });
			x += v * MS;
		});
	});
	parts.forEach((p, j) => {
		const x = 40 + j * 135;
		mx.rect(x, 520, 26, 22, { stroke: pcol[j], fill: pcol[j], fillStyle: j % 2 ? 'hachure' : 'cross-hatch', hachureGap: 5 });
		mx.text(x + 34, 538, p, { size: 17, color: pcol[j] });
	});
	mx.text(40, 586, 'the 1,078 bytes of structure are now a quarter of the best bill: Part 07 goes after them too.', { size: 20, color: PENCIL });

	// ---------------------------------------------------------------- 5. signing speed
	const sp = new Plate(1000, 600, {
		seed: 75,
		title: 'How long one signature takes',
		desc: 'Median signing time on the author\'s machine, logarithmic scale: ECDSA and Ed25519 about 0.03 ms; UOV about 0.03 ms; MAYO and Falcon 0.1 to 0.3 ms; ML-DSA 0.07 to 0.9 ms depending on implementation; RSA 0.3 ms; MQOM 2 ms; SLH-DSA-128f 25 ms; SLH-DSA-128s 530 ms. A server signs once per handshake; a CA and a log once per certificate.',
	});
	const rows = [
		['UOV-Ip-pkc', 0.028, AMBER], ['ECDSA P-256', 0.024, PENCIL], ['Ed25519', 0.032, PENCIL], ['ML-DSA-44', 0.074, BLUE],
		['MAYO-2', 0.115, AMBER], ['Falcon-512', 0.21, GREEN], ['RSA-2048', 0.33, PENCIL], ['SNOVA-24-5-4', 0.44, AMBER],
		['MQOM-L1-short', 2.0, AMBER], ['SLH-DSA-128f', 24.8, BLUE], ['SLH-DSA-128s', 526, BLUE],
	];
	const SX0 = 250, SW = 660;
	const sx = (ms) => SX0 + ((Math.log10(ms) + 2) / 5) * SW; // 0.01 ms .. 1000 ms
	rows.forEach(([name, ms, c], i) => {
		const y = 50 + i * 44;
		sp.text(SX0 - 12, y + 24, name, { anchor: 'end', size: 19, weight: 700, color: c === PENCIL ? INK : c });
		sp.rect(SX0, y + 6, sx(ms) - SX0, 26, { stroke: c, fill: c, fillStyle: 'hachure', hachureGap: 6, strokeWidth: 1.3 });
		sp.text(sx(ms) + 10, y + 26, `${ms < 1 ? ms.toFixed(3) : ms.toFixed(ms < 10 ? 1 : 0)} ms`, { size: 18, color: c === PENCIL ? INK : c });
	});
	for (const [ms, l] of [[0.01, '0.01'], [0.1, '0.1'], [1, '1 ms'], [10, '10'], [100, '100'], [1000, '1 s']]) {
		sp.line(sx(ms), 540, sx(ms), 548, { stroke: INK });
		sp.text(sx(ms), 570, l, { anchor: 'middle', size: 17, color: PENCIL });
	}
	sp.line(SX0, 540, SX0 + SW, 540, { stroke: INK, strokeWidth: 1.4 });
	sp.text(SX0 + SW, 594, 'ML-DSA through liboqs; through OpenSSL it measured up to 7x slower here', { anchor: 'end', size: 17, color: PENCIL });

	return { '06-menu': mn, '06-roles': rl, '06-uniform': un, '06-mixing': mx, '06-speed': sp };
}
