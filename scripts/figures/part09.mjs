// Figures for Root of Trust, part 09: "Tiled logs"
import { Plate, INK, RED, BLUE, GREEN, PENCIL } from './sketch.mjs';

const AMBER = '#b8741a';
const PAPER2 = '#fbf8ef';

export function part09() {
	// ---------------------------------------------------------------- 1. the tile pyramid for 70,000 entries
	const py = new Plate(1000, 600, {
		seed: 101,
		title: 'A log of 70,000 entries, as tiles',
		desc: 'Level 0: 273 full tiles of 256 leaf hashes, then a partial tile of 112. Level 1: one full tile whose 256 hashes are the roots of level 0 tiles 0 to 255, then a partial tile of 17 covering level 0 tiles 256 to 272. Level 2: a partial tile of width 1, the root of level 1 tile 0. Full tiles never change; the partial tiles on the right edge are rewritten as the log grows. Entry bundles sit beside the level 0 tiles.',
	});
	const row = (y, level, items, note) => {
		py.text(30, y + 30, `level ${level}`, { size: 20, weight: 700 });
		let x = 130;
		for (const [w, label, kind] of items) {
			const c = kind === 'full' ? INK : kind === 'partial' ? AMBER : PENCIL;
			const fill = kind === 'full' ? PAPER2 : kind === 'partial' ? 'rgba(184,116,26,0.15)' : 'none';
			if (kind === 'dots') {
				py.text(x + w / 2, y + 30, '...', { anchor: 'middle', size: 24, color: PENCIL });
			} else {
				py.rect(x, y, w, 46, { stroke: c, fill, fillStyle: 'solid', strokeWidth: kind === 'full' ? 1.6 : 2.2 });
				py.text(x + w / 2, y + 29, label, { anchor: 'middle', size: 15, color: c, weight: kind === 'partial' ? 700 : 400 });
			}
			x += w + 8;
		}
		if (note) py.text(970, y + 30, note, { anchor: 'end', size: 16, color: PENCIL });
	};
	row(380, 0, [[90, '0/000', 'full'], [90, '0/001', 'full'], [90, '0/002', 'full'], [60, '', 'dots'], [90, '0/272', 'full'], [110, '273.p/112', 'partial']], '');
	row(250, 1, [[380, '1/000: roots of 0/000 .. 0/255', 'full'], [180, '1/001.p/17', 'partial']], '');
	row(120, 2, [[110, '2/000.p/1', 'partial']], '');
	py.text(130, 465, '256 leaf hashes each, 8,192 bytes', { size: 16, color: PENCIL });
	py.text(778, 465, '112 hashes', { size: 16, color: AMBER, anchor: 'start' });
	py.curvedArrow(175, 376, 160, 330, 200, 300, { stroke: PENCIL, strokeWidth: 1.2 });
	py.text(205, 345, 'root of 0/000 = hash 0 of 1/000', { size: 15, color: PENCIL });
	py.curvedArrow(300, 246, 230, 200, 190, 170, { stroke: PENCIL, strokeWidth: 1.2 });
	py.text(255, 208, 'root of 1/000 = hash 0 of 2/000', { size: 15, color: PENCIL });
	py.rect(130, 500, 840, 40, { stroke: GREEN, fill: 'rgba(60,130,70,0.10)', fillStyle: 'solid', strokeWidth: 1.4 });
	py.text(150, 526, 'tile/entries/<N>: the 256 entries behind level 0 tile N, each with a 2-byte big-endian length', { size: 17, color: GREEN });
	py.text(30, 584, 'full tiles: written once, cached forever. Partial tiles (amber): the right edge, one per level.', { size: 19, weight: 700 });

	// ---------------------------------------------------------------- 2. a path, dissected
	const pa = new Plate(1000, 400, {
		seed: 102,
		title: 'Reading a tile path',
		desc: 'The path tile/0/x001/x234/067.p/8 split into parts: tile is the namespace, 0 is the level, x001/x234/067 is the index 1,234,067 written in groups of three digits with an x on every group but the last, and .p/8 marks a partial tile holding 8 hashes. Without the suffix the tile is full, 256 hashes.',
	});
	const parts = [['tile/', INK, 'namespace'], ['0/', BLUE, 'level L'], ['x001/x234/067', GREEN, 'index N = 1,234,067'], ['.p/8', AMBER, 'partial: 8 hashes']];
	let px = 120;
	parts.forEach(([s, c, l]) => {
		const w = s.length * 30 + 10;
		pa.rect(px, 90, w, 70, { stroke: c, fill: PAPER2, fillStyle: 'solid', strokeWidth: 2 });
		pa.text(px + w / 2, 136, s, { anchor: 'middle', size: 34, weight: 700, color: c });
		pa.text(px + w / 2, 200, l, { anchor: 'middle', size: 18, color: c });
		px += w + 6;
	});
	pa.text(120, 270, 'groups of three digits keep every directory under 1,000 names;', { size: 19 });
	pa.text(120, 298, 'the x marks a directory, so 001 (a file) and x001 (a folder) never collide.', { size: 19 });
	pa.text(120, 350, 'no suffix: a full tile, 256 hashes, 8,192 bytes, never changes.', { size: 19, weight: 700 });

	// ---------------------------------------------------------------- 3. which tiles a proof touches
	const pr = new Plate(1000, 600, {
		seed: 103,
		title: 'Verifying entry 31,337 with four tiles',
		desc: 'The client verifies the checkpoint, then authenticates the right-edge tiles 2/000.p/1, 1/001.p/17 and 0/273.p/112 by rebuilding the root from them. For entry 31,337 it fetches level 0 tile 122, which gives 8 proof hashes inside that tile, and level 1 tile 0, which gives 8 more and also authenticates tile 122: tile 122 must hash to hash 122 of tile 1/000. The last proof hash, the right part of the tree, comes from the right-edge tiles. 17 hashes, 4 tiles beyond the edge.',
	});
	const T = (x, y, w, label, c, sub) => {
		pr.rect(x, y, w, 54, { stroke: c, fill: PAPER2, fillStyle: 'solid', strokeWidth: 2 });
		pr.text(x + w / 2, y + 33, label, { anchor: 'middle', size: 18, weight: 700, color: c });
		if (sub) pr.text(x + w / 2, y + 78, sub, { anchor: 'middle', size: 15, color: PENCIL });
	};
	T(380, 40, 240, 'checkpoint', INK, 'signed: size 70,000, root R');
	T(640, 150, 150, '2/000.p/1', AMBER);
	T(640, 250, 150, '1/001.p/17', AMBER);
	T(640, 350, 150, '0/273.p/112', AMBER);
	pr.text(810, 260, 'right edge:', { size: 17, color: AMBER, weight: 700 });
	pr.text(810, 284, 'together they', { size: 16, color: AMBER });
	pr.text(810, 306, 'must rebuild R', { size: 16, color: AMBER });
	pr.arrow(620, 90, 700, 146, { stroke: AMBER, strokeWidth: 1.4 });
	T(120, 250, 220, '1/000 (full)', BLUE, '8 proof hashes');
	T(120, 400, 220, '0/122 (full)', GREEN, '8 proof hashes, leaf 31,337');
	pr.arrow(230, 396, 230, 330, { stroke: BLUE, strokeWidth: 1.6 });
	pr.text(244, 372, 'MTH(0/122) must equal hash 122 of 1/000', { size: 16, color: BLUE });
	pr.arrow(342, 270, 636, 270, { stroke: BLUE, strokeWidth: 1.4 });
	pr.text(380, 258, 'hash 0 of 2/000 must equal MTH(1/000)', { size: 15, color: BLUE });
	pr.rect(120, 500, 220, 46, { stroke: PENCIL, fill: 'none', strokeWidth: 1.2 });
	pr.text(230, 529, 'entries/122', { anchor: 'middle', size: 17, color: PENCIL });
	pr.arrow(230, 498, 230, 460, { stroke: PENCIL, strokeWidth: 1.2 });
	pr.text(360, 528, 'the entry itself must hash to leaf 31,337 in 0/122', { size: 16, color: PENCIL });
	pr.text(420, 440, '+1 hash: [65536, 70000), from the right edge', { size: 17, color: AMBER, weight: 700 });
	pr.text(30, 586, '17 proof hashes, computed by the client; the server only stores files.', { size: 20, weight: 700 });

	// ---------------------------------------------------------------- 4. caching
	const ca = new Plate(1000, 460, {
		seed: 104,
		title: '5,000 clients, one random entry each',
		desc: 'With a per-proof API, every query names a different entry, so every one is a cache miss and a database lookup: 5,000 at the server. With tiles, the 5,000 clients make 24,666 tile requests between them, but there are only 277 distinct tiles, so 277 requests reach the host and the shared cache answers 98.9 percent.',
	});
	const bars = [['per-proof API: reach the server', 5000, RED], ['tiles: requests by clients', 24666, PENCIL], ['tiles: reach the host', 277, GREEN]];
	const BX = 400, BW = 520, MAX = 25000;
	bars.forEach(([l, n, c], i) => {
		const y = 70 + i * 100;
		ca.text(BX - 16, y + 36, l, { anchor: 'end', size: 19, weight: 700, color: c === PENCIL ? INK : c });
		ca.rect(BX, y + 10, Math.max((n / MAX) * BW, 4), 44, { stroke: c, fill: c, fillStyle: 'hachure', hachureGap: 6, strokeWidth: 1.4 });
		ca.text(BX + Math.max((n / MAX) * BW, 4) + 12, y + 40, n.toLocaleString('en-US'), { size: 20, weight: 700, color: c === PENCIL ? INK : c });
	});
	ca.text(30, 400, 'a tile is the same file for every client, so caches work. A proof is different for every query.', { size: 19, weight: 700 });
	ca.text(30, 432, 'shared cache hit rate with tiles: 98.9%. The log serves 277 files of hashes, not 5,000 proofs.', { size: 18, color: PENCIL });

	// ---------------------------------------------------------------- 5. monitors
	const mo = new Plate(1000, 520, {
		seed: 105,
		title: 'What tailing costs a monitor',
		desc: 'Bytes downloaded per byte of new entries, against entries added per checkpoint, for entries of about 190 bytes. Fetching every partial bundle: 13.7 times at 10 entries per checkpoint, 2.7 at 75, 1.85 at 150, 1.62 at 200, 1.25 at 500, 1.04 at 3,000. Waiting for full bundles and fetching only the partial level 0 tile: 3.1, 1.28, 1.14, 1.10, 1.04, 1.01.',
	});
	const xs = [10, 75, 150, 200, 500, 3000];
	const a1 = [13.68, 2.70, 1.85, 1.62, 1.25, 1.04];
	const a2 = [3.11, 1.28, 1.14, 1.10, 1.04, 1.01];
	const MX0 = 120, MW = 800, MY0 = 420, MH = 330;
	const mx = (v) => MX0 + ((Math.log10(v) - 1) / (Math.log10(3000) - 1)) * MW;
	const my = (r) => MY0 - (Math.log10(r) / Math.log10(16)) * MH;
	mo.line(MX0, MY0, MX0 + MW, MY0, { stroke: INK, strokeWidth: 1.6 });
	mo.line(MX0, MY0, MX0, MY0 - MH - 10, { stroke: INK, strokeWidth: 1.6 });
	for (const v of xs) {
		mo.line(mx(v), MY0, mx(v), MY0 + 8, { stroke: INK });
		mo.text(mx(v), MY0 + 30, v.toLocaleString('en-US'), { anchor: 'middle', size: 16, color: PENCIL });
	}
	for (const r of [1, 2, 4, 8, 16]) {
		mo.line(MX0 - 8, my(r), MX0, my(r), { stroke: INK });
		mo.text(MX0 - 14, my(r) + 6, `${r}x`, { anchor: 'end', size: 16, color: PENCIL });
	}
	const plot = (ys, c, label, ly) => {
		for (let i = 1; i < xs.length; i++) mo.line(mx(xs[i - 1]), my(ys[i - 1]), mx(xs[i]), my(ys[i]), { stroke: c, strokeWidth: 3 });
		xs.forEach((v, i) => mo.circle(mx(v), my(ys[i]), 10, { stroke: c, fill: c, fillStyle: 'solid' }));
		mo.line(600, ly - 6, 640, ly - 6, { stroke: c, strokeWidth: 3 });
		mo.text(650, ly, label, { size: 18, weight: 700, color: c });
	};
	plot(a1, RED, 'fetch every partial bundle', 160);
	plot(a2, GREEN, 'wait for full bundles (spec advice)', 192);
	mo.line(mx(200), MY0, mx(200), MY0 - MH, { stroke: PENCIL, strokeWidth: 1 });
	mo.text(mx(200) + 6, MY0 - MH + 16, 'spec: above 200 per checkpoint, wait', { size: 15, color: PENCIL });
	mo.text(MX0 + MW, MY0 + 64, 'entries added per checkpoint (log scale)', { anchor: 'end', size: 17, color: PENCIL });
	mo.text(30, 504, 'an MTC CA with a checkpoint every 2 s adds thousands per checkpoint: tailing costs almost nothing extra.', { size: 18, weight: 700 });

	return { '09-pyramid': py, '09-path': pa, '09-proof': pr, '09-cache': ca, '09-monitor': mo };
}
