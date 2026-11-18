// Figures for Root of Trust, part 00: "Who do you trust?"
import { Plate, INK, RED, BLUE, GREEN, PENCIL } from './sketch.mjs';

function laptop(p, x, y, label) {
	p.rect(x, y, 120, 78, { fill: '#dfe6e0', fillStyle: 'solid' });
	p.rect(x + 10, y + 10, 100, 58, { stroke: PENCIL, strokeWidth: 1 });
	p.text(x + 60, y + 48, '>_', { anchor: 'middle', size: 30, color: GREEN, weight: 700 });
	p.poly([
		[x - 18, y + 78],
		[x + 138, y + 78],
		[x + 150, y + 96],
		[x - 30, y + 96],
	]);
	p.text(x + 60, y + 130, label, { anchor: 'middle', size: 26, weight: 700 });
}

function server(p, x, y, label) {
	p.rect(x, y, 96, 130, { fill: '#d9dde6', fillStyle: 'solid' });
	for (let i = 0; i < 4; i++) {
		p.line(x + 12, y + 22 + i * 26, x + 84, y + 22 + i * 26, { stroke: PENCIL });
		p.circle(x + 76, y + 32 + i * 26, 6, { stroke: GREEN, fill: GREEN, fillStyle: 'solid' });
	}
	p.text(x + 48, y + 166, label, { anchor: 'middle', size: 26, weight: 700 });
}

function card(p, x, y, w, rows, { title, sigBy, color = INK, fill = '#f7f2e3' } = {}) {
	const h = 46 + rows.length * 30 + 52;
	p.rect(x, y, w, h, { fill, fillStyle: 'solid', stroke: color });
	p.text(x + 14, y + 32, title, { size: 25, weight: 700, color });
	p.line(x + 10, y + 44, x + w - 10, y + 44, { stroke: PENCIL, strokeWidth: 1 });
	rows.forEach(([k, v], i) => {
		p.text(x + 16, y + 74 + i * 30, `${k}:`, { size: 21, color: PENCIL });
		p.text(x + 118, y + 74 + i * 30, v, { size: 22 });
	});
	const sy = y + h - 30;
	p.curve(
		[
			[x + 16, sy + 6],
			[x + 40, sy - 8],
			[x + 62, sy + 8],
			[x + 90, sy - 6],
			[x + 120, sy + 6],
		],
		{ stroke: RED, strokeWidth: 2 },
	);
	p.text(x + 132, sy + 8, `signed by ${sigBy}`, { size: 20, color: RED });
	return h;
}

export function part00() {
	// ---------------------------------------------------------------- 1
	const stranger = new Plate(1000, 430, {
		seed: 11,
		title: 'The stranger problem',
		desc: 'Your laptop wants to talk to example.com over a network it does not control. Mallory sits on the path and can answer instead of the server.',
	});
	laptop(stranger, 70, 120, 'you');
	server(stranger, 820, 90, 'example.com');
	stranger.line(210, 180, 800, 165, { stroke: PENCIL, strokeWidth: 2.2 });
	stranger.text(505, 140, 'the network: routers, wifi, ISPs, ...', { anchor: 'middle', size: 23, color: PENCIL });
	// Mallory
	stranger.circle(505, 275, 54, { stroke: RED, strokeWidth: 2 });
	stranger.text(505, 284, 'M', { anchor: 'middle', size: 34, weight: 700, color: RED });
	stranger.line(505, 248, 500, 174, { stroke: RED, strokeWidth: 1.6 });
	stranger.text(505, 340, 'Mallory: reads, drops, answers', { anchor: 'middle', size: 24, color: RED });
	stranger.text(505, 375, '"hi, I am example.com, here is my key"', { anchor: 'middle', size: 23, color: RED });
	stranger.text(70, 50, 'You have never met this machine.', { size: 30, weight: 700 });
	stranger.text(70, 82, 'Anything that arrives could have been written by anyone on the path.', {
		size: 23,
		color: PENCIL,
	});

	// ---------------------------------------------------------------- 2
	const sig = new Plate(1000, 470, {
		seed: 23,
		title: 'What a signature proves',
		desc: 'Sign takes a message and a secret key and produces a signature. Verify takes the message, the signature and the public key and answers yes or no.',
	});
	sig.text(40, 52, 'A signature binds a message to a key. Nothing more.', { size: 29, weight: 700 });
	// sign box
	sig.rect(330, 110, 150, 80, { stroke: BLUE, strokeWidth: 2 });
	sig.text(405, 160, 'Sign', { anchor: 'middle', size: 32, weight: 700, color: BLUE });
	sig.text(60, 130, 'message m', { size: 25 });
	sig.arrow(185, 125, 325, 140);
	sig.text(60, 200, 'secret key sk', { size: 25, color: RED });
	sig.arrow(210, 192, 325, 170, { stroke: RED });
	sig.arrow(485, 150, 600, 150);
	sig.text(612, 158, 'signature s', { size: 25, weight: 700 });
	// verify box
	sig.rect(330, 285, 150, 80, { stroke: GREEN, strokeWidth: 2 });
	sig.text(405, 335, 'Verify', { anchor: 'middle', size: 32, weight: 700, color: GREEN });
	sig.text(60, 290, 'm, s', { size: 25 });
	sig.arrow(130, 285, 325, 310);
	sig.text(60, 365, 'public key pk', { size: 25, color: GREEN });
	sig.arrow(205, 357, 325, 345, { stroke: GREEN });
	sig.arrow(485, 325, 590, 325);
	sig.text(600, 333, 'yes / no', { size: 27, weight: 700 });
	sig.curvedArrow(690, 175, 760, 230, 495, 300, { stroke: PENCIL, strokeWidth: 1.2 });
	// annotations
	sig.text(735, 300, 'proves:', { size: 23, color: GREEN, weight: 700 });
	sig.text(735, 328, 'whoever holds sk\nsigned exactly m', { size: 22, color: INK });
	sig.text(735, 400, 'does NOT prove:', { size: 23, color: RED, weight: 700 });
	sig.text(735, 428, 'who holds sk', { size: 22, color: INK });
	sig.highlight(728, 408, 160, 30);

	// ---------------------------------------------------------------- 3
	const cert = new Plate(1000, 470, {
		seed: 37,
		title: 'A certificate is a signed sentence',
		desc: 'An index card with subject example.com, a public key, a validity period and an issuer, signed by the issuer.',
	});
	card(
		cert,
		60,
		60,
		520,
		[
			['subject', 'example.com'],
			['key', '3b6a 27bc ... 9e41 (32 bytes)'],
			['valid', '2026-11-17 .. 2027-01-03'],
			['issuer', 'Toy Issuing CA'],
			['may sign?', 'no (not a CA)'],
		],
		{ title: 'certificate', sigBy: 'Toy Issuing CA' },
	);
	cert.text(650, 120, 'read it as one sentence:', { size: 24, color: PENCIL });
	cert.text(
		650,
		160,
		'"I, Toy Issuing CA,\nsay that the key 3b6a...\nbelongs to example.com,\nfrom Nov 17 to Jan 3."',
		{ size: 26, weight: 700, lh: 1.2 },
	);
	cert.arrow(640, 300, 590, 360, { stroke: RED });
	cert.text(660, 330, 'the signature makes the\nsentence tamper-evident.\nit does NOT make it true.', {
		size: 23,
		color: RED,
	});

	// ---------------------------------------------------------------- 4
	const chain = new Plate(1100, 620, {
		seed: 51,
		title: 'A chain of trust ends in a store you configured',
		desc: 'The leaf certificate is signed by an intermediate, the intermediate by a root. The root key sits in a trust store on your device; nothing signs it.',
	});
	const cw = 300;
	card(chain, 40, 210, cw, [['subject', 'example.com'], ['issuer', 'Toy Issuing CA']], { title: 'leaf', sigBy: 'Issuing CA' });
	card(chain, 400, 210, cw, [['subject', 'Toy Issuing CA'], ['issuer', 'Toy Root CA']], { title: 'intermediate', sigBy: 'Root CA' });
	chain.arrow(340, 300, 396, 300, { strokeWidth: 2 });
	chain.text(368, 262, 'checked\nwith', { anchor: 'middle', size: 18, color: PENCIL, lh: 1 });
	// trust store box
	chain.rect(755, 120, 320, 420, { stroke: GREEN, strokeWidth: 2.4 });
	chain.highlight(765, 130, 300, 32, 'rgba(47, 122, 74, 0.18)');
	chain.text(915, 154, 'trust store (YOUR machine)', { anchor: 'middle', size: 23, weight: 700, color: GREEN });
	card(chain, 775, 210, 280, [['subject', 'Toy Root CA'], ['issuer', 'Toy Root CA']], {
		title: 'root',
		sigBy: 'itself (!)',
		color: GREEN,
	});
	chain.arrow(700, 300, 771, 300, { strokeWidth: 2 });
	chain.text(737, 262, 'checked\nwith', { anchor: 'middle', size: 18, color: PENCIL, lh: 1 });
	chain.text(800, 430, 'Mozilla, Apple, Microsoft,\nGoogle, Linux distros\nship this list. You (or\nyour IT) can edit it.', {
		size: 21,
		color: PENCIL,
	});
	chain.text(40, 58, 'Verification walks up. Trust walks down.', { size: 30, weight: 700 });
	chain.text(40, 92, 'Each link is checked with the key in the card above it ...', { size: 23, color: PENCIL });
	chain.text(40, 500, '... until a key you already have.', { size: 26, weight: 700, color: GREEN });
	chain.text(40, 536, 'The self-signature on the root proves nothing: anyone can sign their own card.', {
		size: 22,
		color: RED,
	});
	chain.curvedArrow(640, 545, 720, 470, 785, 360, { stroke: RED, strokeWidth: 1.4 });

	// ---------------------------------------------------------------- 5
	const bill = new Plate(1000, 400, {
		seed: 67,
		title: 'The post-quantum bill',
		desc: 'Leaf public key plus three signatures: 224 bytes with Ed25519, 8572 bytes with ML-DSA-44, about 38 times more.',
	});
	bill.text(40, 50, 'leaf public key + 3 signatures, per handshake', { size: 28, weight: 700 });
	bill.text(40, 82, '(leaf signature by the CA + two transparency-log receipts)', { size: 21, color: PENCIL });
	const scale = 760 / 8572;
	bill.text(40, 160, 'Ed25519', { size: 25, weight: 700 });
	bill.rect(190, 136, 224 * scale + 2, 34, { fill: GREEN, fillStyle: 'solid', stroke: GREEN });
	bill.text(190 + 224 * scale + 16, 162, '224 bytes', { size: 24 });
	bill.text(40, 250, 'ML-DSA-44', { size: 25, weight: 700 });
	bill.rect(190, 226, 8572 * scale, 34, { fill: RED, fillStyle: 'hachure', hachureGap: 6, stroke: RED });
	bill.text(190, 300, '8,572 bytes = 1,312 (key) + 3 x 2,420 (signatures)', { size: 24 });
	bill.text(950, 355, 'about 38x more, before a single byte of web page', {
		anchor: 'end',
		size: 24,
		color: RED,
		weight: 700,
	});

	return {
		'00-stranger': stranger,
		'00-signature': sig,
		'00-certificate': cert,
		'00-chain': chain,
		'00-bill': bill,
	};
}
