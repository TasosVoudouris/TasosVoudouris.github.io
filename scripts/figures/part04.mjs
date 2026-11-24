// Figures for Root of Trust, part 04: "Merkle trees from zero"
import { Plate, INK, RED, BLUE, GREEN, PENCIL } from './sketch.mjs';

const AMBER = '#b8741a';
const PAPER2 = '#fbf8ef';

/** The 7-leaf tree of RFC 6962 §2.1.3, nodes named a..l as in the RFC.
 *  style: name -> { color, fill, label } overrides. Returns node coordinates. */
function tree7(p, { x0 = 90, dx = 130, top = 110, style = {}, leafY = 560, hide = [] } = {}) {
	const lx = (i) => x0 + i * dx;
	const L1 = leafY - 100, L2 = L1 - 110, L3 = L2 - 110, L4 = L3 - 110;
	const pos = {
		a: [lx(0), L1], b: [lx(1), L1], c: [lx(2), L1], d: [lx(3), L1], e: [lx(4), L1], f: [lx(5), L1],
		j: [lx(6), L2],
		g: [(lx(0) + lx(1)) / 2, L2], h: [(lx(2) + lx(3)) / 2, L2], i: [(lx(4) + lx(5)) / 2, L2],
		k: [(lx(0) + lx(3)) / 2, L3], l: [((lx(4) + lx(5)) / 2 + lx(6)) / 2, L3],
		root: [((lx(0) + lx(3)) / 2 + ((lx(4) + lx(5)) / 2 + lx(6)) / 2) / 2, L4],
	};
	const edges = [['root', 'k'], ['root', 'l'], ['k', 'g'], ['k', 'h'], ['l', 'i'], ['l', 'j'],
		['g', 'a'], ['g', 'b'], ['h', 'c'], ['h', 'd'], ['i', 'e'], ['i', 'f']];
	for (const [u, v] of edges) {
		if (hide.includes(u) || hide.includes(v)) continue;
		p.line(pos[u][0], pos[u][1] + 26, pos[v][0], pos[v][1] - 26, { stroke: PENCIL, strokeWidth: 1.3 });
	}
	for (let i = 0; i < 7; i++) {
		const parent = i < 6 ? 'abcdef'[i] : 'j';
		if (hide.includes(parent)) continue;
		p.line(lx(i), leafY - 22, pos[parent][0], pos[parent][1] + 26, { stroke: PENCIL, strokeWidth: 1.1, strokeLineDash: [4, 4] });
		const s = style[`d${i}`] ?? {};
		p.rect(lx(i) - 34, leafY - 20, 68, 40, { stroke: s.color ?? INK, fill: s.fill ?? PAPER2, fillStyle: 'solid', strokeWidth: 1.5 });
		p.text(lx(i), leafY + 8, `d${i}`, { anchor: 'middle', size: 22, weight: 700, color: s.color ?? INK });
	}
	for (const [name, [x, y]] of Object.entries(pos)) {
		if (hide.includes(name)) continue;
		const s = style[name] ?? {};
		p.circle(x, y, name === 'root' ? 60 : 52, { stroke: s.color ?? INK, fill: s.fill ?? PAPER2, fillStyle: 'solid', strokeWidth: s.color ? 2.4 : 1.5 });
		p.text(x, y + 8, s.label ?? (name === 'root' ? 'root' : name), { anchor: 'middle', size: name === 'root' ? 20 : 24, weight: 700, color: s.color ?? INK });
	}
	return pos;
}

export function part04() {
	// ---------------------------------------------------------------- 1. the tree
	const t = new Plate(1000, 680, {
		seed: 51,
		title: 'The Merkle tree of seven entries',
		desc: 'Seven entries d0 to d6. Each leaf hash is SHA-256 of 0x00 followed by the entry: a to f, and j for d6. Each inner node is SHA-256 of 0x01, the left child and the right child: g, h, i, then k and l, then the root. The tree splits at the largest power of two below the size: 7 splits into 4 and 3.',
	});
	tree7(t, { top: 110, style: { root: { color: GREEN } } });
	t.text(40, 50, 'leaf:  H(0x00 || entry)', { size: 25, weight: 700 });
	t.text(460, 50, 'node:  H(0x01 || left || right)', { size: 25, weight: 700 });
	t.text(40, 636, 'split n at the largest power of two below it:  7 = 4 + 3,  then 4 = 2 + 2,  3 = 2 + 1', { size: 22, color: BLUE });
	t.text(890, 430, 'j = d6\'s leaf\nhash, no sibling:\npromoted', { size: 18, color: PENCIL });

	// ---------------------------------------------------------------- 2. inclusion proof
	const inc = new Plate(1000, 700, {
		seed: 52,
		title: 'An inclusion proof for d3',
		desc: 'To prove d3 is in the 7-entry tree, the log sends three hashes: c, g and l. The verifier computes d = H(00 || d3), then h = H(01 || c || d), then k = H(01 || g || h), then root = H(01 || k || l), and compares with the signed root.',
	});
	const sib = { color: RED, fill: '#f8eeec' };
	const comp = { color: BLUE, fill: '#eef1f8' };
	tree7(inc, { style: { d3: comp, d: comp, h: comp, k: comp, root: { ...comp, label: 'root?' }, c: sib, g: sib, l: sib } });
	inc.text(40, 46, 'the log sends [ c, g, l ], in red', { size: 25, weight: 700, color: RED });
	inc.text(40, 80, 'the verifier computes the blue path and compares the root', { size: 23, color: BLUE });
	['d = H(00 || d3)', 'h = H(01 || c || d)', 'k = H(01 || g || h)', 'root = H(01 || k || l)'].forEach((f, i) => inc.text(40 + i * 235, 630, f, { size: 21, color: BLUE }));
	inc.text(40, 668, 'three hashes for seven entries.  a billion entries: thirty.', { size: 22, weight: 700 });

	// ---------------------------------------------------------------- 3. consistency proof
	const cs = new Plate(1000, 770, {
		seed: 53,
		title: 'A consistency proof from 3 entries to 7',
		desc: 'The old tree of 3 entries has root H(g, c). The new tree of 7 has root H(k, l) with k = H(g, h) and h = H(c, d). The proof is c, d, g, l. From c and g the verifier rebuilds the old root; from c, d, g and l it rebuilds the new root. Both must match the signed roots, which proves the first three entries were not changed.',
	});
	tree7(cs, {
		leafY: 610,
		style: {
			c: { color: RED, fill: '#f8eeec' }, d: { color: RED, fill: '#f8eeec' }, g: { color: RED, fill: '#f8eeec' }, l: { color: RED, fill: '#f8eeec' },
			h: { color: BLUE, fill: '#eef1f8' }, k: { color: BLUE, fill: '#eef1f8' }, root: { color: BLUE, fill: '#eef1f8', label: 'new' },
			d0: { color: AMBER }, d1: { color: AMBER }, d2: { color: AMBER },
		},
	});
	cs.highlight(40, 570, 340, 82, 'rgba(184, 116, 26, 0.16)');
	cs.text(46, 566, 'the old log: first 3 entries', { size: 20, color: AMBER, weight: 700 });
	cs.text(40, 46, 'proof = [ c, d, g, l ]', { size: 25, weight: 700, color: RED });
	cs.text(40, 82, 'old root = H(01 || g || c)', { size: 22, color: AMBER });
	cs.text(560, 82, 'check against the old signed head', { size: 20, color: AMBER });
	cs.text(40, 114, 'new root = H(01 || H(01 || g || H(01 || c || d)) || l)', { size: 22, color: BLUE });
	cs.text(560, 114, 'check against the new signed head', { size: 20, color: BLUE });
	cs.text(40, 710, 'the same c and g build both roots: the old tree is still inside the new one.', { size: 22, weight: 700 });
	cs.text(40, 744, 'change any of d0, d1, d2 and no proof can make both roots come out right.', { size: 21, color: PENCIL });

	// ---------------------------------------------------------------- 4. second preimage
	const sp = new Plate(1000, 560, {
		seed: 54,
		title: 'Why leaves and nodes are hashed differently',
		desc: 'Without prefixes, a tree of four entries and a tree of two fake entries can share a root: each fake entry is the 64-byte concatenation of two child hashes, so hashing it as a leaf gives the same value as hashing the inner node. With 0x00 for leaves and 0x01 for nodes, the two computations can never coincide.',
	});
	sp.text(40, 46, 'no prefixes: leaf = H(entry), node = H(left || right)', { size: 25, weight: 700, color: RED });
	const nodeAt = (x, y, label, color = INK, w = 150) => {
		sp.rect(x - w / 2, y - 24, w, 48, { stroke: color, fill: PAPER2, fillStyle: 'solid', strokeWidth: 1.6 });
		sp.text(x, y + 7, label, { anchor: 'middle', size: 20, color, weight: 700 });
	};
	// honest 4-leaf tree
	nodeAt(250, 110, 'root R', GREEN);
	nodeAt(140, 210, 'H(A || B)'); nodeAt(360, 210, 'H(C || D)');
	sp.line(250, 134, 140, 186, { stroke: PENCIL }); sp.line(250, 134, 360, 186, { stroke: PENCIL });
	['A', 'B', 'C', 'D'].forEach((n, i) => {
		const x = 85 + i * 110;
		nodeAt(x, 310, `${n} = H(${n.toLowerCase()})`, INK, 100);
		sp.line(i < 2 ? 140 : 360, 234, x, 286, { stroke: PENCIL });
	});
	sp.text(250, 380, 'four real certificates a, b, c, d', { anchor: 'middle', size: 20, color: PENCIL });
	// forged 2-leaf tree
	nodeAt(750, 110, 'root R', RED);
	nodeAt(640, 210, 'H(x)', RED); nodeAt(860, 210, 'H(y)', RED);
	sp.line(750, 134, 640, 186, { stroke: PENCIL }); sp.line(750, 134, 860, 186, { stroke: PENCIL });
	nodeAt(640, 310, 'x = A || B', RED, 160); nodeAt(860, 310, 'y = C || D', RED, 160);
	sp.line(640, 234, 640, 286, { stroke: PENCIL }); sp.line(860, 234, 860, 286, { stroke: PENCIL });
	sp.text(750, 380, 'two "entries" of 64 bytes each, never logged', { anchor: 'middle', size: 20, color: RED });
	sp.text(500, 120, '=', { anchor: 'middle', size: 48, weight: 700, color: RED });
	sp.text(40, 450, 'H(x) = H(A || B): the fake leaf hashes exactly like the real inner node.', { size: 22 });
	sp.text(40, 490, 'RFC 6962: leaf = H(0x00 || entry), node = H(0x01 || L || R).', { size: 22, weight: 700, color: GREEN });
	sp.text(40, 526, 'a leaf hash and a node hash now start from different first bytes: they cannot be swapped.', { size: 21, color: GREEN });

	// ---------------------------------------------------------------- 5. sizes
	const sz = new Plate(1000, 520, {
		seed: 55,
		title: 'Proof size grows with the logarithm',
		desc: 'An inclusion proof needs one 32-byte hash per level: 96 bytes for 8 entries, 320 for a thousand, 640 for a million, 960 for a billion, 1,280 for about a trillion. One ML-DSA-44 signature is 2,420 bytes.',
	});
	const X0 = 120, Y0 = 430, W = 820, H = 330;
	const xOf = (lg) => X0 + (lg / 42) * W;
	const yOf = (bytes) => Y0 - (bytes / 2600) * H;
	sz.line(X0, Y0, X0 + W, Y0, { stroke: INK, strokeWidth: 1.6 });
	sz.line(X0, Y0, X0, Y0 - H - 10, { stroke: INK, strokeWidth: 1.6 });
	sz.text(X0 + W, Y0 + 66, 'entries in the log (log scale)', { anchor: 'end', size: 20, color: PENCIL });
	sz.text(X0 - 10, Y0 - H - 20, 'bytes', { size: 20, color: PENCIL });
	const pts = [[3, '8'], [10, '1 thousand'], [20, '1 million'], [30, '1 billion'], [40, '1 trillion']];
	sz.line(xOf(0), yOf(0), xOf(41), yOf(41 * 32), { stroke: BLUE, strokeWidth: 2.4 });
	for (const [lg, label] of pts) {
		const b = lg * 32;
		sz.circle(xOf(lg), yOf(b), 12, { stroke: BLUE, fill: BLUE, fillStyle: 'solid' });
		sz.text(xOf(lg), Y0 + 30, label, { anchor: 'middle', size: 19 });
		sz.text(xOf(lg) - 8, yOf(b) - 16, `${b.toLocaleString('en-US')} B`, { anchor: 'end', size: 20, color: BLUE, weight: 700 });
	}
	sz.line(X0, yOf(2420), X0 + W, yOf(2420), { stroke: RED, strokeWidth: 2, strokeLineDash: [10, 6] });
	sz.text(X0 + 10, yOf(2420) - 12, 'one ML-DSA-44 signature: 2,420 B', { size: 21, color: RED, weight: 700 });
	sz.text(X0 + 10, yOf(1800), 'every doubling of the log adds one hash: 32 bytes', { size: 21, color: BLUE });

	return {
		'04-tree': t,
		'04-inclusion': inc,
		'04-consistency': cs,
		'04-second-preimage': sp,
		'04-sizes': sz,
	};
}
