// Figures for Root of Trust, part 01: "A certificate, byte by byte"
import { Plate, INK, RED, BLUE, GREEN, PENCIL } from './sketch.mjs';

const AMBER = '#b8741a';

/** A row of hand-drawn byte boxes. Returns the x after the last box. */
function bytes(p, x, y, list, { w = 52, h = 46, color = INK, fill = '#f7f2e3', size = 26 } = {}) {
	for (const b of list) {
		p.rect(x, y, w, h, { fill, fillStyle: 'solid', stroke: color });
		p.text(x + w / 2, y + h * 0.68, b, { anchor: 'middle', size, weight: 700, color });
		x += w + 6;
	}
	return x;
}

/** Eight bit cells with group braces underneath. groups: [[from, to, label, color]] */
function bits(p, x, y, pattern, groups, { w = 40 } = {}) {
	[...pattern].forEach((b, i) => {
		p.rect(x + i * w, y, w, 44, { fill: '#fbf8ef', fillStyle: 'solid', stroke: PENCIL, strokeWidth: 1.2 });
		p.text(x + i * w + w / 2, y + 31, b, { anchor: 'middle', size: 26, weight: 700 });
	});
	for (const [a, b, label, color] of groups) {
		const x1 = x + a * w + 4;
		const x2 = x + (b + 1) * w - 4;
		p.line(x1, y + 54, x2, y + 54, { stroke: color, strokeWidth: 2 });
		p.line(x1, y + 48, x1, y + 56, { stroke: color, strokeWidth: 2 });
		p.line(x2, y + 48, x2, y + 56, { stroke: color, strokeWidth: 2 });
		p.text((x1 + x2) / 2, y + 82, label, { anchor: 'middle', size: 21, color, lh: 1.0 });
	}
}

export function part01() {
	// ---------------------------------------------------------------- 1. TLV
	const tlv = new Plate(1000, 560, {
		seed: 21,
		title: 'Tag, length, value',
		desc: 'Every DER element is a tag byte, a length, and that many value bytes. The tag byte packs a class, a constructed flag and a number: 0x30 is a universal constructed SEQUENCE, 0xA3 is the context-specific constructed tag [3].',
	});
	tlv.text(40, 50, 'every DER element, everywhere:', { size: 28, weight: 700 });
	let x = bytes(tlv, 60, 78, ['30'], { color: BLUE });
	x = bytes(tlv, x + 14, 78, ['82', '01', '52'], { color: AMBER });
	tlv.rect(x + 14, 78, 330, 46, { fill: '#eef3ee', fillStyle: 'solid', stroke: GREEN });
	tlv.text(x + 179, 109, '338 bytes of content ...', { anchor: 'middle', size: 25, color: GREEN, weight: 700 });
	tlv.text(86, 158, 'T', { anchor: 'middle', size: 34, weight: 700, color: BLUE });
	tlv.text(229, 158, 'L', { anchor: 'middle', size: 34, weight: 700, color: AMBER });
	tlv.text(x + 179, 158, 'V', { anchor: 'middle', size: 34, weight: 700, color: GREEN });
	tlv.text(760, 150, 'and V may itself be\na list of more TLVs', { size: 22, color: PENCIL });
	tlv.curvedArrow(752, 146, 700, 150, 662, 118, { stroke: PENCIL, strokeWidth: 1.2 });

	tlv.line(40, 190, 960, 190, { stroke: PENCIL, strokeWidth: 0.8 });
	tlv.text(40, 232, 'zoom into the tag byte:', { size: 26, weight: 700 });

	const groups = (num, numColor) => [
		[0, 1, 'class', RED],
		[2, 2, 'P/C', BLUE],
		[3, 7, num, numColor],
	];
	tlv.text(60, 300, '0x30', { size: 34, weight: 700, color: BLUE });
	bits(tlv, 150, 270, '00110000', groups('number 16', GREEN));
	tlv.text(500, 284, '00 = universal', { size: 23, color: RED });
	tlv.text(500, 312, '1 = constructed (holds TLVs)', { size: 23, color: BLUE });
	tlv.text(500, 340, '10000 = 16 = SEQUENCE', { size: 23, color: GREEN });

	tlv.text(60, 450, '0xA3', { size: 34, weight: 700, color: RED });
	bits(tlv, 150, 420, '10100011', groups('number 3', GREEN));
	tlv.text(500, 434, '10 = context-specific', { size: 23, color: RED });
	tlv.text(500, 462, '1 = constructed', { size: 23, color: BLUE });
	tlv.text(500, 490, '00011 = 3, written [3]', { size: 23, color: GREEN });
	tlv.text(500, 530, 'in a certificate, [3] means "extensions follow"', { size: 21, color: PENCIL });

	// ---------------------------------------------------------------- 2. lengths
	const len = new Plate(1000, 470, {
		seed: 22,
		title: 'Short and long length forms',
		desc: 'A length under 128 fits in one byte with the top bit clear. Otherwise the first byte has the top bit set and says how many length bytes follow: 82 01 52 means two bytes follow, 0x0152 = 338.',
	});
	len.text(40, 50, 'short form: length 0 ... 127', { size: 28, weight: 700, color: GREEN });
	bytes(len, 60, 76, ['05'], { color: AMBER });
	bits(len, 160, 76, '00000101', [
		[0, 0, 'top bit 0', RED],
		[1, 7, 'the length itself: 5', GREEN],
	], { w: 36 });
	len.text(520, 106, 'one byte, done', { size: 24, color: PENCIL });

	len.line(40, 196, 960, 196, { stroke: PENCIL, strokeWidth: 0.8 });
	len.text(40, 240, 'long form: length 128 and up', { size: 28, weight: 700, color: AMBER });
	x = bytes(len, 60, 266, ['82'], { color: RED });
	bytes(len, x + 10, 266, ['01', '52'], { color: AMBER });
	bits(len, 280, 266, '10000010', [
		[0, 0, 'top bit 1', RED],
		[1, 7, '2 length bytes follow', AMBER],
	], { w: 36 });
	len.text(620, 290, '0x0152 = 1*256 + 82', { size: 25, color: AMBER, weight: 700 });
	len.text(620, 322, '= 338 bytes of value', { size: 25, color: AMBER, weight: 700 });
	len.highlight(54, 386, 600, 34);
	len.text(60, 412, 'DER: always the shortest form. "81 05" is legal BER, illegal DER', { size: 23, color: RED });
	len.text(60, 446, 'and "80" (indefinite length, ends with 00 00) is banned outright', { size: 21, color: PENCIL });

	// ---------------------------------------------------------------- 3. OIDs
	const oid = new Plate(1000, 560, {
		seed: 23,
		title: 'Encoding an object identifier',
		desc: 'The OID 1.3.101.112 (Ed25519) becomes 2B 65 70: the first two arcs fold into 40*1+3 = 43 = 0x2B, the rest are base-128 digits. The arc 840 needs two digits, 6 and 72, written 86 48 with the top bit marking "more follows".',
	});
	oid.text(40, 50, 'Ed25519 is 1 . 3 . 101 . 112', { size: 30, weight: 700 });
	oid.text(196, 112, '40 x 1 + 3 = 43', { size: 26, color: BLUE, anchor: 'middle' });
	oid.text(400, 112, '101', { size: 26, color: GREEN, anchor: 'middle' });
	oid.text(560, 112, '112', { size: 26, color: GREEN, anchor: 'middle' });
	oid.arrow(196, 124, 196, 160, { stroke: BLUE });
	oid.arrow(400, 124, 400, 160, { stroke: GREEN });
	oid.arrow(560, 124, 560, 160, { stroke: GREEN });
	bytes(oid, 60, 168, ['06', '03'], { color: PENCIL, w: 46 });
	bytes(oid, 170, 168, ['2B'], { color: BLUE, w: 52 });
	bytes(oid, 374, 168, ['65'], { color: GREEN, w: 52 });
	bytes(oid, 534, 168, ['70'], { color: GREEN, w: 52 });
	oid.text(650, 200, 'all under 128: one byte each', { size: 23, color: PENCIL });
	oid.text(80, 248, 'tag 06, length 3', { size: 20, color: PENCIL });

	oid.line(40, 280, 960, 280, { stroke: PENCIL, strokeWidth: 0.8 });
	oid.text(40, 324, 'big arcs: base 128, top bit = "more digits follow"', { size: 27, weight: 700 });
	oid.text(60, 378, '840 = 6 x 128 + 72', { size: 27, color: RED, weight: 700 });
	bits(oid, 60, 400, '10000110', [
		[0, 0, 'more', RED],
		[1, 7, '6', GREEN],
	], { w: 34 });
	bits(oid, 360, 400, '01001000', [
		[0, 0, 'last', BLUE],
		[1, 7, '72', GREEN],
	], { w: 34 });
	oid.text(196, 520, '= 0x86', { anchor: 'middle', size: 26, weight: 700, color: RED });
	oid.text(496, 520, '= 0x48', { anchor: 'middle', size: 26, weight: 700, color: BLUE });
	oid.text(680, 400, 'ML-DSA-44 is\n2.16.840.1.101.3.4.3.17', { size: 24 });
	oid.text(680, 470, '60 86 48 01 65 03 04 03 11', { size: 24, weight: 700, color: RED });
	oid.text(680, 502, '9 bytes, versus 3 for Ed25519', { size: 21, color: PENCIL });

	// ---------------------------------------------------------------- 4. nesting
	const nest = new Plate(1000, 740, {
		seed: 24,
		title: 'The 342-byte certificate as nested boxes',
		desc: 'The outer SEQUENCE holds three things: tbsCertificate (264 bytes, the part the CA signs, offsets 4 to 267), the signature algorithm (7 bytes) and the signature (67 bytes). Inside the signed part sit version, serial, algorithm, issuer, validity, subject, public key and extensions.',
	});
	nest.rect(30, 30, 940, 680, { stroke: INK, strokeWidth: 2 });
	nest.text(50, 66, 'Certificate   SEQUENCE   342 bytes   @0', { size: 27, weight: 700 });

	nest.highlight(58, 86, 660, 476, 'rgba(198, 52, 43, 0.10)');
	nest.rect(60, 88, 656, 472, { stroke: RED, strokeWidth: 2.2 });
	nest.text(80, 124, 'tbsCertificate   264 bytes   @4', { size: 26, weight: 700, color: RED });
	const fields = [
		['version  [0] v3', '@8', 5],
		['serialNumber', '@13', 19],
		['signature  (ed25519)', '@32', 7],
		['issuer  CN=Root of Trust Toy CA', '@39', 33],
		['validity  2026-11-18 .. 2027-01-03', '@72', 32],
		['subject  CN=example.com', '@104', 24],
		['subjectPublicKeyInfo', '@128', 44],
		['extensions  [3]', '@172', 96],
	];
	let y = 142;
	for (const [label, off, size] of fields) {
		nest.rect(84, y, 608, 40, { stroke: PENCIL, strokeWidth: 1.2, fill: '#fbf8ef', fillStyle: 'solid' });
		nest.text(100, y + 28, label, { size: 23 });
		nest.text(560, y + 28, off, { size: 21, color: PENCIL, anchor: 'end' });
		nest.text(676, y + 28, `${size} B`, { size: 23, weight: 700, anchor: 'end', color: BLUE });
		y += 50;
	}
	nest.text(750, 170, 'the CA signs\nexactly these\n264 bytes,\nheader included', { size: 25, color: RED, weight: 700 });
	nest.curvedArrow(800, 300, 790, 360, 724, 380, { stroke: RED, strokeWidth: 1.6 });
	nest.text(740, 450, 'SAN, basicConstraints,\nkeyUsage, extKeyUsage', { size: 21, color: PENCIL });
	nest.curvedArrow(760, 484, 740, 520, 700, 515, { stroke: PENCIL, strokeWidth: 1.2 });

	nest.rect(60, 584, 300, 44, { stroke: INK, fill: '#fbf8ef', fillStyle: 'solid' });
	nest.text(76, 614, 'signatureAlgorithm  @268', { size: 23 });
	nest.text(346, 614, '7 B', { size: 23, weight: 700, anchor: 'end', color: BLUE });
	nest.rect(380, 584, 336, 44, { stroke: GREEN, strokeWidth: 2, fill: '#eef3ee', fillStyle: 'solid' });
	nest.text(396, 614, 'signatureValue  @275', { size: 23, color: GREEN });
	nest.text(702, 614, '67 B', { size: 23, weight: 700, anchor: 'end', color: GREEN });
	nest.text(80, 676, 'algorithm said twice: once inside the signed bytes, once outside', { size: 22, color: PENCIL });
	nest.text(740, 600, '64-byte Ed25519\nsignature over\nthe red box', { size: 22, color: GREEN });

	// ---------------------------------------------------------------- 5. sizes
	const sizes = new Plate(1000, 430, {
		seed: 25,
		title: 'Same certificate, two signature algorithms',
		desc: 'Drawn to scale. Ed25519: 246 bytes of structure, 32 of key, 64 of signature, 342 total. ML-DSA-44: 270 bytes of structure, 1312 of key, 2420 of signature, 4002 total.',
	});
	const S = 880 / 4002;
	const bar = (y, parts, label, total) => {
		let bx = 60;
		sizes.text(60, y - 14, label, { size: 26, weight: 700 });
		for (const [n, color, fill] of parts) {
			const w = Math.max(n * S, 4);
			sizes.rect(bx, y, w, 50, { stroke: color, fill, fillStyle: 'hachure', hachureGap: 6, strokeWidth: 1.6 });
			bx += w;
		}
		sizes.text(bx + 12, y + 33, total, { size: 26, weight: 700 });
	};
	bar(80, [[246, PENCIL, PENCIL], [32, BLUE, BLUE], [64, GREEN, GREEN]], 'Ed25519', '342 B');
	bar(220, [[270, PENCIL, PENCIL], [1312, BLUE, BLUE], [2420, GREEN, GREEN]], 'ML-DSA-44', '');
	sizes.text(940, 206, '4002 B', { size: 26, weight: 700, anchor: 'end' });
	sizes.text(60 + (270 + 656) * S, 300, 'public key 1312', { size: 23, anchor: 'middle', color: BLUE });
	sizes.text(60 + (1582 + 1210) * S, 300, 'signature 2420', { size: 23, anchor: 'middle', color: GREEN });
	sizes.text(60, 300, 'structure 270', { size: 21, color: PENCIL });
	sizes.text(60, 360, 'the ASN.1 skeleton barely moves (246 to 270 bytes).', { size: 24 });
	sizes.text(60, 392, 'the cryptography is what grows: 96 bytes become 3732.', { size: 24, color: RED, weight: 700 });

	return {
		'01-tlv': tlv,
		'01-lengths': len,
		'01-oid': oid,
		'01-nesting': nest,
		'01-sizes': sizes,
	};
}
