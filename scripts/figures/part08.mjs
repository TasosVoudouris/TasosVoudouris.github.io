// Figures for Root of Trust, part 08: "Landmarks you can check"
import { Plate, INK, RED, BLUE, GREEN, PENCIL } from './sketch.mjs';

const AMBER = '#b8741a';
const PAPER2 = '#fbf8ef';
const fmt = (n) => Math.round(n).toLocaleString('en-US');

export function part08() {
	// ---------------------------------------------------------------- 1. the proof in the tree of size 14
	const tr = new Plate(1000, 600, {
		seed: 91,
		title: 'A subtree consistency proof, tree of size 14',
		desc: 'The tree of 14 entries: root [0,14) splits into [0,8) and [8,14); [8,14) into [8,12) and [12,14); [12,14) into entries 12 and 13. The subtree [8,13) is highlighted. Its proof is four hashes: entry 12 (inside the subtree, the starting point), entry 13 (a right sibling outside it), [8,12) (a left sibling inside it) and [0,8) (a left sibling outside it). From these the verifier rebuilds both the subtree hash and the root.',
	});
	const LX = (i) => 60 + i * 62;
	const LY = 470;
	const node = (x, y, label, o = {}) => {
		tr.rect(x - 52, y - 22, 104, 44, { stroke: o.c ?? INK, fill: o.fill ?? PAPER2, fillStyle: 'solid', strokeWidth: o.w ?? 1.5 });
		tr.text(x, y + 7, label, { anchor: 'middle', size: 18, color: o.c ?? INK, weight: o.bold ? 700 : 400 });
	};
	tr.highlight(LX(8) - 28, LY - 28, LX(12) - LX(8) + 56, 56, 'rgba(60,130,70,0.18)');
	tr.text((LX(8) + LX(12)) / 2, LY + 66, 'the subtree [8, 13)', { anchor: 'middle', size: 19, color: GREEN, weight: 700 });
	for (let i = 0; i < 14; i++) {
		const proof = i === 12 || i === 13;
		tr.circle(LX(i), LY, 34, { stroke: proof ? RED : INK, fill: proof ? 'rgba(190,40,40,0.15)' : PAPER2, fillStyle: 'solid', strokeWidth: proof ? 2.4 : 1.2 });
		tr.text(LX(i), LY + 6, String(i), { anchor: 'middle', size: 17 });
	}
	const P = {
		root: [(LX(0) + LX(13)) / 2 + 120, 70], a08: [(LX(0) + LX(7)) / 2, 200], a814: [(LX(8) + LX(13)) / 2, 200],
		a812: [(LX(8) + LX(11)) / 2, 320], a1214: [(LX(12) + LX(13)) / 2, 320],
	};
	const edge = (a, b) => tr.line(a[0], a[1] + 22, b[0], b[1] - 22, { stroke: PENCIL, strokeWidth: 1.2 });
	edge(P.root, P.a08); edge(P.root, P.a814); edge(P.a814, P.a812); edge(P.a814, P.a1214);
	for (let i = 0; i < 8; i++) tr.line(P.a08[0], P.a08[1] + 22, LX(i), LY - 18, { stroke: 'rgba(110,110,110,0.35)', strokeWidth: 0.8 });
	for (let i = 8; i < 12; i++) tr.line(P.a812[0], P.a812[1] + 22, LX(i), LY - 18, { stroke: 'rgba(110,110,110,0.35)', strokeWidth: 0.8 });
	tr.line(P.a1214[0], P.a1214[1] + 22, LX(12), LY - 18, { stroke: PENCIL, strokeWidth: 1.2 });
	tr.line(P.a1214[0], P.a1214[1] + 22, LX(13), LY - 18, { stroke: PENCIL, strokeWidth: 1.2 });
	node(...P.root, 'root [0,14)', { bold: true });
	node(...P.a08, '[0, 8)', { c: RED, fill: 'rgba(190,40,40,0.12)', w: 2.4, bold: true });
	node(...P.a814, '[8, 14)');
	node(...P.a812, '[8, 12)', { c: RED, fill: 'rgba(190,40,40,0.12)', w: 2.4, bold: true });
	node(...P.a1214, '[12, 14)');
	tr.text(30, 40, 'proof, in order:', { size: 20, weight: 700, color: RED });
	tr.text(30, 66, '1. entry 12   (inside: the starting point)', { size: 18, color: RED });
	tr.text(30, 90, '2. entry 13   (right sibling, outside)', { size: 18, color: RED });
	tr.text(30, 114, '3. [8, 12)    (left sibling, inside)', { size: 18, color: RED });
	tr.text(30, 138, '4. [0, 8)     (left sibling, outside)', { size: 18, color: RED });
	tr.text(40, 580, 'inside hashes rebuild the subtree; all four rebuild the root. The verifier checks both at once.', { size: 20, weight: 700 });

	// ---------------------------------------------------------------- 2. two hashes climbing
	const wk = new Plate(1000, 560, {
		seed: 92,
		title: 'Two running hashes, one walk',
		desc: 'Verification of [8,13) in the tree of size 14. Start: fr and sr are both the hash of entry 12. Step 1, entry 13 is a right sibling: only sr changes, sr = H(12, 13) = [12,14). Step 2, [8,12) is a left sibling inside the subtree: fr = H([8,12), 12) = [8,13) and sr = H([8,12), [12,14)) = [8,14). Step 3, [0,8) is a left sibling outside: only sr changes, sr = H([0,8), [8,14)) = the root. Accept if fr equals the claimed subtree hash, sr equals the root, and the position counter tn has reached zero.',
	});
	const rows = [
		['start', 'entry 12', 'entry 12', 'fn 8 · sn 12 · tn 13', INK],
		['entry 13, RIGHT sibling', 'unchanged', 'H(12, 13) = [12,14)', 'fn 4 · sn 6 · tn 6', BLUE],
		['[8,12), LEFT, inside', 'H([8,12), 12) = [8,13)', 'H([8,12), [12,14)) = [8,14)', 'fn 1 · sn 1 · tn 1', GREEN],
		['[0,8), LEFT, outside', 'unchanged', 'H([0,8), [8,14)) = root', 'fn 0 · sn 0 · tn 0', BLUE],
	];
	wk.text(250, 54, 'fr: the subtree', { size: 21, weight: 700, color: GREEN });
	wk.text(530, 54, 'sr: the whole tree', { size: 21, weight: 700, color: BLUE });
	wk.text(820, 54, 'positions', { size: 21, weight: 700, color: PENCIL });
	rows.forEach(([step, fr, sr, pos, c], i) => {
		const y = 80 + i * 92;
		wk.rect(30, y, 940, 76, { stroke: c, fill: PAPER2, fillStyle: 'solid', strokeWidth: 1.4 });
		wk.text(44, y + 46, step, { size: 18, weight: 700, color: c });
		wk.text(250, y + 46, fr, { size: 18, color: fr === 'unchanged' ? PENCIL : GREEN });
		wk.text(530, y + 46, sr, { size: 18, color: BLUE });
		wk.text(820, y + 46, pos, { size: 17, color: PENCIL });
	});
	wk.text(30, 470, 'accept when fr = claimed [8,13), sr = root, tn = 0', { size: 22, weight: 700 });
	wk.text(30, 506, 'a right sibling lies outside the subtree, so it never touches fr. The bits of sn decide left or right.', { size: 18, color: PENCIL });

	// ---------------------------------------------------------------- 3. what the update service checks
	const vs = new Plate(1000, 620, {
		seed: 93,
		title: 'What stands behind a trusted landmark',
		desc: 'The update service checks three things before shipping landmark subtrees. One, a reference checkpoint at least as large as the latest landmark. Two, each cosigner vouches for it: the CA and witness A cosign it directly; witness B cosigned a larger checkpoint, linked to the reference by an RFC 9162 consistency proof. Three, every landmark subtree has a subtree consistency proof against the reference. Only then do browsers get the list of trusted subtree hashes, about 10.8 KB per CA.',
	});
	const bx = (x, y, w, h, t, s, c) => {
		vs.rect(x, y, w, h, { stroke: c, fill: PAPER2, fillStyle: 'solid', strokeWidth: 2 });
		vs.text(x + w / 2, y + 34, t, { anchor: 'middle', size: 21, weight: 700, color: c });
		if (s) vs.text(x + w / 2, y + 62, s, { anchor: 'middle', size: 16, color: PENCIL });
	};
	bx(360, 40, 280, 100, 'reference checkpoint', 'size n >= latest landmark, root R', INK);
	bx(30, 40, 220, 90, 'CA cosigner', 'cosigns [0, n) directly', BLUE);
	bx(30, 170, 220, 90, 'witness A', 'cosigns [0, n) directly', GREEN);
	bx(30, 300, 220, 110, 'witness B', 'cosigned [0, n\') with\nn\' > n', GREEN);
	vs.arrow(252, 85, 356, 85, { stroke: BLUE, strokeWidth: 1.6 });
	vs.arrow(252, 210, 356, 120, { stroke: GREEN, strokeWidth: 1.6 });
	vs.arrow(252, 350, 380, 142, { stroke: GREEN, strokeWidth: 1.6 });
	vs.text(300, 300, 'consistency proof', { size: 16, color: GREEN, anchor: 'middle' });
	vs.text(300, 318, 'n -> n\'', { size: 16, color: GREEN, anchor: 'middle' });
	for (let i = 0; i < 4; i++) {
		const x = 660 + (i % 2) * 160, y = 200 + Math.floor(i / 2) * 110;
		vs.rect(x, y, 140, 80, { stroke: AMBER, fill: PAPER2, fillStyle: 'solid', strokeWidth: 1.6 });
		vs.text(x + 70, y + 34, `landmark ${['L-3', 'L-2', 'L-1', 'L'][i]}`, { anchor: 'middle', size: 18, weight: 700, color: AMBER });
		vs.text(x + 70, y + 60, '2 subtrees', { anchor: 'middle', size: 15, color: PENCIL });
	}
	vs.arrow(642, 110, 700, 196, { stroke: AMBER, strokeWidth: 1.6 });
	vs.text(700, 150, 'subtree consistency', { size: 16, color: AMBER });
	vs.text(700, 170, 'proof per subtree', { size: 16, color: AMBER });
	vs.rect(300, 460, 400, 80, { stroke: INK, fill: 'rgba(60,130,70,0.12)', fillStyle: 'solid', strokeWidth: 2 });
	vs.text(500, 494, 'trusted subtrees -> browsers', { anchor: 'middle', size: 21, weight: 700, color: GREEN });
	vs.text(500, 522, '(log, start, end, hash): ~10.8 KB per CA', { anchor: 'middle', size: 16, color: PENCIL });
	vs.arrow(500, 144, 500, 456, { stroke: INK, strokeWidth: 1.6 });
	vs.arrow(800, 420, 620, 458, { stroke: AMBER, strokeWidth: 1.4 });
	vs.text(30, 600, 'the cosigners never signed the landmark subtrees. They signed checkpoints; proofs connect the two.', { size: 19, weight: 700 });

	// ---------------------------------------------------------------- 4. the draft's lagging example
	const lg = new Plate(1000, 540, {
		seed: 94,
		title: 'Witnesses behind: keep what can be proved',
		desc: 'Landmarks at tree sizes 200, 300, 400 and 500. The witnesses have only checked a checkpoint of size 350. Landmarks 1 and 2 lie inside it and are kept; landmarks 3 and 4 lie beyond it and are discarded, together with everything newer. Below, a forged hash for landmark 2 discards landmarks 2, 3 and 4 and keeps landmark 1.',
	});
	const X0 = 80, W = 840;
	const x = (v) => X0 + (v / 520) * W;
	const axis = (y) => {
		lg.line(X0, y, X0 + W, y, { stroke: INK, strokeWidth: 1.8 });
		for (const v of [0, 100, 200, 300, 400, 500]) {
			lg.line(x(v), y - 6, x(v), y + 6, { stroke: INK });
			lg.text(x(v), y + 28, String(v), { anchor: 'middle', size: 16, color: PENCIL });
		}
	};
	const band = (y, lms, keep) => {
		lms.forEach(([a, b, n], i) => {
			const ok = keep.includes(n);
			lg.rect(x(a), y - 50, x(b) - x(a), 36, { stroke: ok ? GREEN : RED, fill: ok ? 'rgba(60,130,70,0.14)' : 'rgba(190,40,40,0.10)', fillStyle: 'solid', strokeWidth: 1.8 });
			lg.text((x(a) + x(b)) / 2, y - 26, `landmark ${n}`, { anchor: 'middle', size: 17, weight: 700, color: ok ? GREEN : RED });
		});
	};
	const L = [[0, 200, 1], [200, 300, 2], [300, 400, 3], [400, 500, 4]];
	lg.text(X0, 60, 'witnesses have only checked 350', { size: 20, weight: 700 });
	band(150, L, [1, 2]); axis(160);
	lg.line(x(350), 80, x(350), 200, { stroke: BLUE, strokeWidth: 2.4 });
	lg.text(x(350) + 8, 96, 'reference checkpoint 350', { size: 17, color: BLUE, weight: 700 });
	lg.text(X0, 300, 'the CA ships a forged hash for landmark 2', { size: 20, weight: 700 });
	band(390, L, [1]); axis(400);
	lg.text(x(250), 446, 'inconsistent', { anchor: 'middle', size: 17, color: RED, weight: 700 });
	lg.text(X0, 510, 'a failure discards that landmark and every newer one; older landmarks stay trusted (§7.4).', { size: 19, color: PENCIL });

	// ---------------------------------------------------------------- 5. stale clients
	const st = new Plate(1000, 580, {
		seed: 95,
		title: 'How stale can a client be?',
		desc: 'Share of handshakes that can use a landmark-relative certificate, against hours since the client last updated its landmarks. Seven-day certificates renewed at 75 percent, both kept until expiry, one hour from landmark to client. The share is 100 percent up to about 40 hours, then falls linearly: 94 percent at 48 hours, 75 at 72, 56 at 96, 38 at 120, 18 at 144, 0 at 168. The expected authentication bytes rise from 4,296 to 11,417 along the same line.',
	});
	const pts = [[0, 1], [12, 1], [24, 1], [40, 1], [48, 0.942], [72, 0.751], [96, 0.564], [120, 0.375], [144, 0.182], [168, 0]];
	const SX0 = 110, SW = 800, SY0 = 470, SH = 380;
	const sx = (h) => SX0 + (h / 180) * SW, sy = (f) => SY0 - f * SH;
	st.line(SX0, SY0, SX0 + SW, SY0, { stroke: INK, strokeWidth: 1.6 });
	st.line(SX0, SY0, SX0, SY0 - SH - 10, { stroke: INK, strokeWidth: 1.6 });
	for (const h of [0, 24, 48, 72, 96, 120, 144, 168]) {
		st.line(sx(h), SY0, sx(h), SY0 + 8, { stroke: INK });
		st.text(sx(h), SY0 + 30, `${h} h`, { anchor: 'middle', size: 16, color: PENCIL });
	}
	for (const f of [0, 0.25, 0.5, 0.75, 1]) {
		st.line(SX0 - 8, sy(f), SX0, sy(f), { stroke: INK });
		st.text(SX0 - 14, sy(f) + 6, `${f * 100}%`, { anchor: 'end', size: 16, color: PENCIL });
	}
	for (let i = 1; i < pts.length; i++) st.line(sx(pts[i - 1][0]), sy(pts[i - 1][1]), sx(pts[i][0]), sy(pts[i][1]), { stroke: GREEN, strokeWidth: 3 });
	for (const [h, f] of pts) st.circle(sx(h), sy(f), 10, { stroke: GREEN, fill: GREEN, fillStyle: 'solid' });
	st.highlight(sx(0), sy(1) - 6, sx(42) - sx(0), SH + 6, 'rgba(60,130,70,0.10)');
	st.text(sx(21), sy(1) + 40, 'always small:', { anchor: 'middle', size: 18, weight: 700, color: GREEN });
	st.text(sx(21), sy(1) + 62, '42 h overlap', { anchor: 'middle', size: 17, color: GREEN });
	st.text(sx(21), sy(1) + 84, 'minus delays', { anchor: 'middle', size: 17, color: GREEN });
	for (const [h, f, b] of [[72, 0.751, '6,068 B'], [120, 0.375, '8,743 B']]) st.text(sx(h) + 14, sy(f) - 10, b, { size: 17, color: INK });
	st.text(sx(168) - 4, sy(0) - 34, '11,417 B', { anchor: 'end', size: 17, color: RED, weight: 700 });
	st.text(sx(0) + 14, sy(1) - 14, '4,296 B', { size: 17, color: GREEN, weight: 700 });
	st.text(SX0 + SW, SY0 + 64, 'hours since the client last received landmarks', { anchor: 'end', size: 18, color: PENCIL });
	st.text(SX0 - 80, 60, 'landmark-relative share', { size: 18, color: PENCIL });

	return { '08-tree': tr, '08-walk': wk, '08-service': vs, '08-lagging': lg, '08-stale': st };
}
