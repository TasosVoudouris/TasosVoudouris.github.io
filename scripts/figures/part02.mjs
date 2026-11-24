// Figures for Root of Trust, part 02: "The handshake bill"
import { Plate, INK, RED, BLUE, GREEN, PENCIL } from './sketch.mjs';

const AMBER = '#b8741a';
const PAPER2 = '#fbf8ef';

function box(p, x, y, w, h, label, { color = INK, size = 22, fill = PAPER2, weight = 400, sub } = {}) {
	p.rect(x, y, w, h, { stroke: color, fill, fillStyle: 'solid', strokeWidth: 1.6 });
	p.text(x + w / 2, y + (sub ? h / 2 - 2 : h / 2 + size * 0.33), label, { anchor: 'middle', size, color, weight });
	if (sub) p.text(x + w / 2, y + h / 2 + 22, sub, { anchor: 'middle', size: size - 4, color: PENCIL });
}

export function part02() {
	// ---------------------------------------------------------------- 1. the handshake
	const hs = new Plate(1000, 700, {
		seed: 31,
		title: 'A TLS 1.3 handshake',
		desc: 'The client sends ClientHello with its key shares. The server answers in one flight: ServerHello, then encrypted EncryptedExtensions, Certificate, CertificateVerify and Finished. Certificate and CertificateVerify are the authentication bytes. The client answers with Finished and data can flow.',
	});
	const CX = 140, SX = 860;
	hs.text(CX, 50, 'client', { anchor: 'middle', size: 30, weight: 700 });
	hs.text(SX, 50, 'server', { anchor: 'middle', size: 30, weight: 700 });
	hs.line(CX, 66, CX, 670, { stroke: PENCIL, strokeWidth: 1.4 });
	hs.line(SX, 66, SX, 670, { stroke: PENCIL, strokeWidth: 1.4 });

	hs.arrow(CX + 6, 104, SX - 6, 134, { stroke: INK, strokeWidth: 2 });
	hs.text(500, 104, 'ClientHello   + key shares', { anchor: 'middle', size: 24, weight: 700 });
	hs.text(500, 160, 'hybrid ML-KEM share: 1,216 B   (X25519 alone: 32 B)', { anchor: 'middle', size: 20, color: PENCIL });

	// the server flight
	const rows = [
		['ServerHello', '+ key share (1,120 B hybrid)', INK, false],
		['EncryptedExtensions', '', INK, true],
		['Certificate', 'the chain: leaf + intermediate', RED, true],
		['CertificateVerify', 'leaf key signs the transcript', RED, true],
		['Finished', 'MAC over everything so far', INK, true],
	];
	let y = 230;
	hs.highlight(600, 322, 250, 122, 'rgba(198, 52, 43, 0.10)');
	for (const [name, note, color, enc] of rows) {
		hs.text(SX - 26, y, (enc ? '{ ' : '') + name + (enc ? ' }' : ''), { anchor: 'end', size: 24, color, weight: 700 });
		if (note) hs.text(SX - 26, y + 24, note, { anchor: 'end', size: 19, color: PENCIL });
		y += 62;
	}
	hs.arrow(SX - 6, 520, CX + 6, 550, { stroke: INK, strokeWidth: 2 });
	hs.text(190, 300, 'one flight,\nno waiting in\nbetween', { size: 22, color: BLUE });
	hs.line(320, 272, 860, 272, { stroke: GREEN, strokeWidth: 1.4, strokeLineDash: [8, 6] });
	hs.text(330, 296, 'encrypted from here on  { }', { size: 19, color: GREEN });
	hs.text(330, 372, 'the authentication bytes:\nthis part is the bill', { size: 22, color: RED, weight: 700 });
	hs.arrow(530, 382, 592, 382, { stroke: RED, strokeWidth: 1.6 });

	hs.arrow(CX + 6, 590, SX - 6, 616, { stroke: INK, strokeWidth: 2 });
	hs.text(500, 592, '{ Finished }', { anchor: 'middle', size: 24, weight: 700 });
	hs.text(500, 660, 'application data, both ways', { anchor: 'middle', size: 22, color: GREEN });
	hs.line(CX + 30, 668, SX - 30, 668, { stroke: GREEN, strokeWidth: 1.6 });

	// ---------------------------------------------------------------- 2. the Certificate message
	const cm = new Plate(1000, 470, {
		seed: 32,
		title: 'Inside the Certificate message',
		desc: 'The ML-DSA-44 Certificate message is 13,374 bytes: a 4-byte handshake header, a 1-byte empty request context, a 3-byte list length, then each certificate as a 3-byte length, the DER bytes, and a 2-byte empty extensions block. The root is not sent.',
	});
	cm.text(40, 46, 'the ML-DSA-44 chain, as OpenSSL sent it: 13,374 bytes', { size: 26, weight: 700 });
	const seg = (x, w, top, bottom, color, fill = PAPER2, size = 18) => {
		cm.rect(x, 80, w, 60, { stroke: color, fill, fillStyle: 'solid', strokeWidth: 1.6 });
		cm.text(x + w / 2, 116, top, { anchor: 'middle', size, weight: 700, color });
		if (bottom) cm.text(x + w / 2, 168, bottom, { anchor: 'middle', size: 18, color: PENCIL, lh: 1.05 });
		return x + w + 6;
	};
	let cx = 30;
	cx = seg(cx, 104, '0b 00 34 3a', 'type 11,\nlength', PENCIL);
	cx = seg(cx, 36, '00', 'ctx', PENCIL);
	cx = seg(cx, 84, '00 34 36', 'list\nlength', PENCIL);
	cx = seg(cx, 80, '00 23 96', '9,110', BLUE);
	cx = seg(cx, 266, 'leaf certificate, DER', 'key + CA signature\n+ 2 SCTs', BLUE, '#eef1f8', 20);
	cx = seg(cx, 54, '00 00', 'ext', PENCIL);
	cx = seg(cx, 80, '00 10 96', '4,246', GREEN);
	cx = seg(cx, 160, 'intermediate', 'DER, then 00 00', GREEN, '#eef3ee', 20);

	cm.text(40, 250, 'every length is a fixed-width big-endian integer, TLS style:', { size: 23 });
	cm.text(60, 286, 'vec8 = 1 length byte,  vec16 = 2,  vec24 = 3.   0x2396 = 9,110.  0x1096 = 4,246.', { size: 22, color: BLUE });
	cm.text(40, 334, 'overhead of the message itself: 4 + 1 + 3 + 2 x (3 + 2) = 18 bytes.', { size: 23 });
	cm.text(40, 370, 'the other 13,356 are the two certificates.', { size: 23, weight: 700 });
	cm.rect(640, 392, 320, 56, { stroke: PENCIL, strokeWidth: 1.2, strokeLineDash: [6, 5] });
	cm.text(800, 428, 'root: NOT sent (4,066 B)', { anchor: 'middle', size: 22, color: PENCIL });
	cm.text(40, 430, 'the client already holds the root; sending it would prove nothing', { size: 20, color: PENCIL });

	// ---------------------------------------------------------------- 3. five signatures, two keys
	const sg = new Plate(1000, 640, {
		seed: 33,
		title: 'Five signatures and two public keys',
		desc: 'The root signs the intermediate (1). The intermediate signs the leaf (2). Two CT logs sign SCTs embedded in the leaf (3, 4). The leaf key signs the handshake transcript in CertificateVerify (5). The intermediate and leaf public keys travel too; the root stays home.',
	});
	box(sg, 40, 60, 250, 90, 'root', { color: PENCIL, size: 26, sub: 'in the client already' });
	sg.rect(370, 50, 290, 150, { stroke: GREEN, strokeWidth: 2, fill: '#eef3ee', fillStyle: 'solid' });
	sg.text(515, 86, 'intermediate cert', { anchor: 'middle', size: 25, weight: 700, color: GREEN });
	sg.text(390, 126, 'public key', { size: 22, color: BLUE });
	sg.text(390, 162, 'signature (1)', { size: 22, color: RED });
	sg.text(640, 126, '1,312', { size: 22, anchor: 'end', color: BLUE });
	sg.text(640, 162, '2,420', { size: 22, anchor: 'end', color: RED });
	sg.curvedArrow(290, 120, 330, 150, 380, 160, { stroke: RED, strokeWidth: 1.8 });
	sg.text(296, 196, 'signs', { size: 20, color: RED });

	sg.rect(370, 260, 290, 230, { stroke: BLUE, strokeWidth: 2, fill: '#eef1f8', fillStyle: 'solid' });
	sg.text(515, 296, 'leaf cert', { anchor: 'middle', size: 25, weight: 700, color: BLUE });
	const leafRows = [['public key', '1,312', BLUE], ['signature (2)', '2,420', RED], ['SCT, log A (3)', '2,420', AMBER], ['SCT, log B (4)', '2,420', AMBER]];
	leafRows.forEach(([l, n, c], i) => {
		sg.text(390, 338 + i * 38, l, { size: 22, color: c });
		sg.text(640, 338 + i * 38, n, { size: 22, color: c, anchor: 'end' });
	});
	sg.curvedArrow(520, 200, 500, 230, 520, 258, { stroke: RED, strokeWidth: 1.8 });
	sg.text(530, 238, 'signs (2)', { size: 20, color: RED });

	box(sg, 740, 300, 220, 80, 'CT log A', { color: AMBER, size: 22 });
	box(sg, 740, 400, 220, 80, 'CT log B', { color: AMBER, size: 22 });
	sg.arrow(740, 352, 664, 414, { stroke: AMBER, strokeWidth: 1.6 });
	sg.arrow(740, 440, 664, 452, { stroke: AMBER, strokeWidth: 1.6 });

	sg.rect(370, 540, 290, 70, { stroke: RED, strokeWidth: 2, fill: '#f8eeec', fillStyle: 'solid' });
	sg.text(390, 584, 'CertificateVerify (5)', { size: 22, color: RED, weight: 700 });
	sg.text(640, 584, '2,420', { size: 22, color: RED, anchor: 'end' });
	sg.curvedArrow(370, 330, 320, 450, 368, 570, { stroke: BLUE, strokeWidth: 1.8 });
	sg.text(200, 452, 'the leaf key\nsigns this\nhandshake', { size: 21, color: BLUE });
	sg.text(700, 560, 'made fresh for\nevery connection', { size: 20, color: PENCIL });
	sg.text(40, 300, 'ML-DSA-44 sizes:\n2 x 1,312\n+ 5 x 2,420\n= 14,724 bytes', { size: 23, weight: 700 });

	// ---------------------------------------------------------------- 4. the flights against the limits
	const fl = new Plate(1000, 560, {
		seed: 34,
		title: 'Server first flight against the transport limits',
		desc: 'Measured server first flights with hybrid key exchange: classical 3,020 bytes; ML-DSA-44 leaf only 12,918; ML-DSA-44 full chain 17,169; ML-DSA-65 full chain 22,916. A QUIC server may send about 7,200 bytes before the client proves its address; TCP sends about 14,600 bytes in its first window.',
	});
	const X0 = 260, SCALE = 680 / 24000;
	const bars = [
		['classical', 3020, GREEN],
		['ML-DSA-44, leaf only', 12918, AMBER],
		['ML-DSA-44, full chain', 17169, RED],
		['ML-DSA-65, full chain', 22916, RED],
	];
	bars.forEach(([label, n, c], i) => {
		const y = 90 + i * 92;
		fl.text(X0 - 16, y + 24, label, { anchor: 'end', size: 23, weight: 700 });
		fl.text(X0 - 16, y + 50, `${n.toLocaleString('en-US')} B`, { anchor: 'end', size: 22, color: c, weight: 700 });
		fl.rect(X0, y, n * SCALE, 52, { stroke: c, fill: c, fillStyle: 'hachure', hachureGap: 7, strokeWidth: 1.6 });
	});
	const vline = (n, label, color) => {
		const x = X0 + n * SCALE;
		fl.line(x, 64, x, 470, { stroke: color, strokeWidth: 2.2, strokeLineDash: [10, 6] });
		fl.text(x, 500, label, { anchor: 'middle', size: 21, color, weight: 700, lh: 1.05 });
	};
	vline(7200, 'QUIC: ~7,200\n(3 x what the\nclient sent)', BLUE);
	vline(14600, 'TCP: 10 segments\n~14,600 B', INK);
	fl.text(X0, 50, 'bytes the server sends before it must wait for the client', { size: 22, color: PENCIL });

	// ---------------------------------------------------------------- 5. the extra round trip
	const rt = new Plate(1000, 560, {
		seed: 35,
		title: 'What happens when the flight does not fit',
		desc: 'Left: the whole server flight fits in the first congestion window and the client can finish after one round trip. Right: the server sends ten segments, waits for the client to acknowledge them, and only then sends the rest, so the handshake takes an extra round trip.',
	});
	const lane = (x0, title, extra) => {
		const c = x0 + 60, s = x0 + 380;
		rt.text(x0 + 220, 46, title, { anchor: 'middle', size: 25, weight: 700, color: extra ? RED : GREEN });
		rt.text(c, 84, 'client', { anchor: 'middle', size: 21 });
		rt.text(s, 84, 'server', { anchor: 'middle', size: 21 });
		rt.line(c, 96, c, 530, { stroke: PENCIL, strokeWidth: 1.2 });
		rt.line(s, 96, s, 530, { stroke: PENCIL, strokeWidth: 1.2 });
		rt.arrow(c + 4, 116, s - 4, 156, { stroke: INK, strokeWidth: 1.6 });
		rt.text(x0 + 220, 124, 'ClientHello', { anchor: 'middle', size: 19 });
		if (!extra) {
			for (let k = 0; k < 4; k++) rt.arrow(s - 4, 166 + k * 10, c + 4, 206 + k * 10, { stroke: GREEN, strokeWidth: 1.2 });
			rt.text(x0 + 236, 182, 'whole flight', { anchor: 'middle', size: 19, color: GREEN });
			rt.arrow(c + 4, 270, s - 4, 310, { stroke: INK, strokeWidth: 1.6 });
			rt.text(x0 + 220, 280, 'Finished + request', { anchor: 'middle', size: 19 });
			rt.text(x0 + 220, 400, 'one round trip', { anchor: 'middle', size: 24, weight: 700, color: GREEN });
		} else {
			for (let k = 0; k < 4; k++) rt.arrow(s - 4, 166 + k * 10, c + 4, 206 + k * 10, { stroke: AMBER, strokeWidth: 1.2 });
			rt.text(x0 + 236, 182, '10 segments', { anchor: 'middle', size: 19, color: AMBER });
			rt.arrow(c + 4, 250, s - 4, 290, { stroke: PENCIL, strokeWidth: 1.4 });
			rt.text(x0 + 220, 258, 'ACK', { anchor: 'middle', size: 19, color: PENCIL });
			rt.text(s + 10, 270, 'waits', { size: 19, color: RED });
			for (let k = 0; k < 3; k++) rt.arrow(s - 4, 300 + k * 10, c + 4, 340 + k * 10, { stroke: RED, strokeWidth: 1.2 });
			rt.text(x0 + 236, 316, 'the rest', { anchor: 'middle', size: 19, color: RED });
			rt.arrow(c + 4, 400, s - 4, 440, { stroke: INK, strokeWidth: 1.6 });
			rt.text(x0 + 220, 410, 'Finished + request', { anchor: 'middle', size: 19 });
			rt.text(x0 + 220, 500, 'two round trips', { anchor: 'middle', size: 24, weight: 700, color: RED });
		}
	};
	lane(20, 'flight fits', false);
	lane(520, 'flight too big', true);
	rt.line(500, 40, 500, 530, { stroke: PENCIL, strokeWidth: 0.8 });

	return {
		'02-handshake': hs,
		'02-certificate-message': cm,
		'02-signatures': sg,
		'02-flights': fl,
		'02-round-trips': rt,
	};
}
