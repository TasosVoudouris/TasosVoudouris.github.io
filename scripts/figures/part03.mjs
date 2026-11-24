// Figures for Root of Trust, part 03: "When authorities lie"
import { Plate, INK, RED, BLUE, GREEN, PENCIL } from './sketch.mjs';

const AMBER = '#b8741a';
const PAPER2 = '#fbf8ef';

function box(p, x, y, w, h, label, { color = INK, size = 22, fill = PAPER2, weight = 700, sub, subSize } = {}) {
	p.rect(x, y, w, h, { stroke: color, fill, fillStyle: 'solid', strokeWidth: 1.6 });
	p.text(x + w / 2, y + (sub ? h / 2 - 4 : h / 2 + size * 0.33), label, { anchor: 'middle', size, color, weight });
	if (sub) p.text(x + w / 2, y + h / 2 + 20, sub, { anchor: 'middle', size: subSize ?? size - 5, color: PENCIL, lh: 1.05 });
}

export function part03() {
	// ---------------------------------------------------------------- 1. any CA, any name
	const any = new Plate(1000, 520, {
		seed: 41,
		title: 'Any trusted CA can sign for any name',
		desc: 'A browser trusts every root in its store equally, and by default any of them, or any intermediate below them, may issue a certificate for any domain. The security of example.com is the security of the weakest CA in the store, not of the CA example.com chose.',
	});
	box(any, 380, 400, 240, 80, 'example.com', { color: BLUE, size: 26 });
	any.text(366, 470, 'chose CA "B"\nand pays it', { anchor: 'end', size: 20, color: BLUE });
	const cas = [
		['A', 70, 70, INK], ['B', 230, 40, GREEN], ['C', 390, 70, INK], ['D', 550, 40, INK],
		['E', 710, 70, INK], ['F', 860, 40, RED],
	];
	for (const [n, x, y, c] of cas) {
		box(any, x - 50, y, 100, 64, `CA ${n}`, { color: c, size: 22 });
		any.arrow(x, y + 66, 500 + (x - 500) * 0.3, 396, { stroke: c === RED ? RED : c === GREEN ? GREEN : PENCIL, strokeWidth: c === INK ? 1.1 : 1.8 });
	}
	any.text(900, 132, 'breached,\nor careless,\nor coerced', { anchor: 'middle', size: 21, color: RED, weight: 700 });
	any.text(30, 360, 'all equally\ntrusted by the\nbrowser', { size: 22, color: PENCIL });
	any.text(760, 300, 'one signature from F\nis as good as one from B', { size: 22, color: RED });

	// ---------------------------------------------------------------- 2. timeline
	const tl = new Plate(1000, 640, {
		seed: 42,
		title: 'Fifteen years of authorities that lied',
		desc: 'Timeline: 2011 Comodo RA breach and DigiNotar breach; 2012 TURKTRUST intermediate used against google.com (found December); 2013 RFC 6962; 2015 CNNIC and MCS Holdings, and a Symantec test certificate for google.com found in CT logs; 2018 Chrome requires CT for new certificates and distrusts Symantec; 2024 Chrome distrusts Entrust; 2025 Firefox enforces CT and twelve Fina certificates for 1.1.1.1 are found in CT logs.',
	});
	const Y = 320, X0 = 60, X1 = 950;
	const xOf = (yr) => X0 + ((yr - 2010.6) / (2025.9 - 2010.6)) * (X1 - X0);
	tl.line(X0, Y, X1, Y, { stroke: INK, strokeWidth: 2.2 });
	for (let yr = 2011; yr <= 2025; yr++) {
		const x = xOf(yr);
		tl.line(x, Y - 8, x, Y + 8, { stroke: INK, strokeWidth: 1.4 });
		if (yr % 2 === 1) tl.text(x, Y + 34, `${yr}`, { anchor: 'middle', size: 20, color: PENCIL });
	}
	const ev = [
		[2011.2, 'Comodo: RA account\nbreached, 9 certs', RED, -1, 220],
		[2011.55, 'DigiNotar: 531+ certs,\n*.google.com used\nagainst Iran', RED, 1, 400],
		[2012.98, 'TURKTRUST: stray\nintermediate signs\n*.google.com', RED, -1, 120],
		[2013.45, 'RFC 6962:\nCertificate\nTransparency', GREEN, 1, 470],
		[2015.22, 'CNNIC / MCS:\nMITM box signs\nGoogle names', RED, -1, 220],
		[2015.7, 'Symantec test cert\nfor google.com,\nfound IN CT', AMBER, 1, 400],
		[2018.3, 'Chrome requires CT;\ndistrusts Symantec', GREEN, -1, 120],
		[2024.5, 'Chrome distrusts\nEntrust (cutoff\nby SCT time)', AMBER, -1, 220],
		[2025.1, 'Firefox 135\nenforces CT', GREEN, -1, 120],
		[2025.68, '12 Fina certs for\n1.1.1.1, found\nIN CT', AMBER, 1, 400],
	];
	for (const [t, label, c, dir, ty] of ev) {
		const x = xOf(t);
		tl.circle(x, Y, 13, { stroke: c, fill: c, fillStyle: 'solid' });
		const yEnd = dir < 0 ? ty + 80 : ty - 28;
		tl.line(x, Y + (dir < 0 ? -10 : 10), x, yEnd, { stroke: c, strokeWidth: 1.2 });
		const anchor = x > 820 ? 'end' : x < 140 ? 'start' : 'middle';
		tl.text(x + (anchor === 'end' ? 10 : anchor === 'start' ? -10 : 0), ty, label, { anchor, size: 19, color: c, lh: 1.05 });
	}
	tl.text(X0, 600, 'red: a CA issued what it should not   amber: caught or punished through CT   green: the system changing', { size: 19, color: PENCIL });

	// ---------------------------------------------------------------- 3. how CT works
	const ctf = new Plate(1000, 640, {
		seed: 43,
		title: 'How Certificate Transparency works',
		desc: 'The CA sends a precertificate to two or more logs run by different operators. Each log returns a signed certificate timestamp (SCT), a promise to publish within 24 hours. The CA embeds the SCTs in the final certificate. The browser refuses certificates without enough valid SCTs. Monitors read the logs and tell domain owners about every certificate for their names.',
	});
	box(ctf, 40, 60, 180, 80, 'CA', { color: INK, size: 28 });
	box(ctf, 420, 30, 200, 70, 'log 1', { color: AMBER, size: 24, sub: 'operator X' });
	box(ctf, 420, 130, 200, 70, 'log 2', { color: AMBER, size: 24, sub: 'operator Y' });
	ctf.arrow(222, 86, 416, 62, { stroke: INK, strokeWidth: 1.6 });
	ctf.arrow(222, 104, 416, 160, { stroke: INK, strokeWidth: 1.6 });
	ctf.text(250, 52, '1. precertificate', { size: 20 });
	ctf.curvedArrow(418, 88, 320, 120, 224, 124, { stroke: AMBER, strokeWidth: 1.6 });
	ctf.curvedArrow(418, 190, 300, 190, 200, 144, { stroke: AMBER, strokeWidth: 1.6 });
	ctf.text(240, 220, '2. SCTs: "we promise to\npublish this within 24 h"', { size: 20, color: AMBER });

	box(ctf, 40, 300, 180, 90, 'certificate', { color: BLUE, size: 24, sub: '+ 2 SCTs inside' });
	ctf.arrow(130, 142, 130, 296, { stroke: INK, strokeWidth: 1.6 });
	ctf.text(140, 270, '3. embed, sign', { size: 20 });
	box(ctf, 330, 310, 160, 70, 'server', { color: INK, size: 24 });
	box(ctf, 600, 310, 170, 70, 'browser', { color: INK, size: 24 });
	ctf.arrow(222, 345, 326, 345, { stroke: BLUE, strokeWidth: 1.6 });
	ctf.arrow(492, 345, 596, 345, { stroke: BLUE, strokeWidth: 1.6 });
	ctf.text(520, 420, '4. checks the chain AND\n>= 2 valid SCTs from\n>= 2 log operators', { size: 20, color: GREEN });

	box(ctf, 760, 70, 200, 80, 'monitor', { color: GREEN, size: 24, sub: 'reads every entry' });
	ctf.arrow(624, 70, 756, 100, { stroke: GREEN, strokeWidth: 1.6 });
	ctf.arrow(624, 168, 756, 124, { stroke: GREEN, strokeWidth: 1.6 });
	box(ctf, 760, 210, 200, 70, 'domain owner', { color: GREEN, size: 22 });
	ctf.arrow(860, 152, 860, 206, { stroke: GREEN, strokeWidth: 1.6 });
	ctf.text(880, 192, 'alert', { size: 19, color: GREEN });
	ctf.text(40, 500, 'the log does not judge: it accepts any chain to a trusted root.', { size: 22 });
	ctf.text(40, 536, 'it only makes issuance public. Judging is the monitors\' job.', { size: 22 });
	ctf.text(40, 590, 'and nothing here, yet, proves a log kept its promise: Parts 04 and 05.', { size: 22, color: RED, weight: 700 });

	// ---------------------------------------------------------------- 4. detection, not prevention
	const dn = new Plate(1000, 420, {
		seed: 44,
		title: 'Detection, not prevention',
		desc: 'Timeline of a rogue certificate under CT. At issuance the logs return SCTs and the browser accepts it. Within the maximum merge delay of 24 hours the logs publish it; a monitor alerts the owner; the certificate is revoked or the CA is distrusted. The attacker had a window of use, but could not stay hidden.',
	});
	const T0 = 80, T1 = 920, LY = 210;
	dn.line(T0, LY, T1, LY, { stroke: INK, strokeWidth: 2 });
	dn.arrow(T1 - 10, LY, T1 + 20, LY, { stroke: INK, strokeWidth: 2 });
	dn.highlight(T0 + 10, LY - 50, 420, 40, 'rgba(198, 52, 43, 0.14)');
	dn.text(T0 + 220, LY - 22, 'window of use: up to the MMD (24 h)', { anchor: 'middle', size: 20, color: RED, weight: 700 });
	const marks = [
		[T0 + 10, 'rogue cert issued,\nlogged, SCTs signed', RED],
		[T0 + 430, 'log publishes it\n(by the deadline)', AMBER],
		[T0 + 610, 'monitor:\n"unknown key!"', GREEN],
		[T0 + 790, 'revoked;\nCA investigated', GREEN],
	];
	for (const [x, label, c] of marks) {
		dn.circle(x, LY, 14, { stroke: c, fill: c, fillStyle: 'solid' });
		dn.text(x, LY + 50, label, { anchor: 'middle', size: 20, color: c, lh: 1.05 });
	}
	dn.text(T0, 70, 'before CT: the first row is the whole story, and it stays secret.', { size: 22, color: PENCIL });
	dn.text(T0, 360, 'CT cannot stop the first use. It guarantees there is a second act.', { size: 22, weight: 700 });

	// ---------------------------------------------------------------- 5. who must lie
	const wl = new Plate(1000, 470, {
		seed: 45,
		title: 'Who has to lie for a rogue certificate to stay secret',
		desc: 'Before CT, one CA lying is enough. With CT and two required SCTs from different operators, the CA and every log that issued an SCT must lie. Even then nothing in the SCT shows the broken promise; Merkle tree proofs (Part 04) and signed, witnessed tree heads (Part 05) close that gap.',
	});
	const panel = (x, title, rows, verdict, vc) => {
		wl.rect(x, 50, 290, 330, { stroke: PENCIL, strokeWidth: 1.2 });
		wl.text(x + 145, 90, title, { anchor: 'middle', size: 24, weight: 700 });
		rows.forEach(([who, c], i) => {
			wl.rect(x + 30, 120 + i * 62, 230, 48, { stroke: c, fill: PAPER2, fillStyle: 'solid', strokeWidth: 1.6 });
			wl.text(x + 145, 152 + i * 62, who, { anchor: 'middle', size: 21, color: c, weight: 700 });
		});
		wl.text(x + 145, 420, verdict, { anchor: 'middle', size: 21, color: vc, weight: 700, lh: 1.05 });
	};
	panel(30, 'before CT', [['1 CA lies', RED]], 'enough to stay\nsecret', RED);
	panel(355, 'CT today', [['1 CA lies', RED], ['log of operator X lies', RED], ['log of operator Y lies', RED]],
		'all three: still secret\n(the toy\'s scenario 8)', AMBER);
	panel(680, 'with proofs', [['CA lies', RED], ['logs lie', RED], ['witnesses see', GREEN], ['one view for all', GREEN]],
		'a broken promise\nbecomes evidence', GREEN);
	wl.arrow(322, 215, 352, 215, { stroke: PENCIL, strokeWidth: 1.4 });
	wl.arrow(647, 215, 677, 215, { stroke: PENCIL, strokeWidth: 1.4 });

	return {
		'03-any-ca': any,
		'03-timeline': tl,
		'03-ct-flow': ctf,
		'03-detection': dn,
		'03-who-must-lie': wl,
	};
}
