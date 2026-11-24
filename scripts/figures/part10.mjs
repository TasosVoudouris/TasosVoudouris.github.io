// Figures for Root of Trust, part 10: "A log that never forks"
import { Plate, INK, RED, BLUE, GREEN, PENCIL } from './sketch.mjs';

const AMBER = '#b8741a';
const PAPER2 = '#fbf8ef';

export function part10() {
	// ---------------------------------------------------------------- 1. how a crash forks the naive log
	const fk = new Plate(1000, 560, {
		seed: 111,
		title: 'One crash, two histories',
		desc: 'The naive log publishes checkpoint 587, then crashes before uploading that round of tiles. On restart it rebuilds from the entries it finds in storage, which end at 315, and the clients whose submissions were in flight retry in a different order. Its next checkpoint, 640, puts certificate 359 at position 315 where the published checkpoint 587 had certificate 316. Two signed checkpoints disagree about the past: a fork.',
	});
	const X0 = 80;
	fk.line(X0, 280, 420, 280, { stroke: INK, strokeWidth: 3 });
	fk.text(X0, 262, 'entries 0 .. 314: in storage, in every history', { size: 17, color: PENCIL });
	fk.circle(420, 280, 16, { stroke: INK, fill: INK, fillStyle: 'solid' });
	fk.line(420, 280, 880, 150, { stroke: BLUE, strokeWidth: 3 });
	fk.line(420, 280, 880, 410, { stroke: RED, strokeWidth: 3 });
	fk.rect(620, 90, 300, 60, { stroke: BLUE, fill: PAPER2, fillStyle: 'solid', strokeWidth: 2 });
	fk.text(770, 118, 'checkpoint 587, published', { anchor: 'middle', size: 18, weight: 700, color: BLUE });
	fk.text(770, 140, 'entry 315 = cert 316', { anchor: 'middle', size: 16, color: BLUE });
	fk.rect(620, 420, 300, 60, { stroke: RED, fill: PAPER2, fillStyle: 'solid', strokeWidth: 2 });
	fk.text(770, 448, 'checkpoint 640, after restart', { anchor: 'middle', size: 18, weight: 700, color: RED });
	fk.text(770, 470, 'entry 315 = cert 359', { anchor: 'middle', size: 16, color: RED });
	fk.text(440, 200, 'crash after "publish",', { size: 17, color: AMBER, weight: 700 });
	fk.text(440, 222, 'before "tiles"', { size: 17, color: AMBER, weight: 700 });
	fk.text(440, 370, 'restart: rebuild from storage,', { size: 17, color: RED });
	fk.text(440, 392, 'retries arrive in a new order', { size: 17, color: RED });
	fk.text(X0, 540, 'both are signed by the same key. A witness that cosigned 587 can never cosign 640.', { size: 20, weight: 700 });

	// ---------------------------------------------------------------- 2. the five orders
	const od = new Plate(1000, 600, {
		seed: 112,
		title: 'Five orders for the same five steps',
		desc: 'Naive: sign, publish, tiles; a crash between publish and tiles forks. Tiles first: tiles, sign, publish; safe from crashes, but storage is the only record, so a rollback or a twin forks. Lock first: sign, lock, tiles, publish; a crash between lock and tiles leaves a locked checkpoint with no tiles, stuck. Sunlight: tiles, sign, lock, publish; recovers from every crash, but tiles beyond the lock get rewritten, which conditional writes refuse. Staged: stage tiles under a private name for this exact tree, sign, lock, copy, publish; recovery rolls the copy forward.',
	});
	const proto = [
		['naive', ['sign', 'publish', 'tiles'], [1, 2], RED, 'forks on a crash'],
		['tiles first', ['tiles', 'sign', 'publish'], null, AMBER, 'forks on rollback, twins'],
		['lock first', ['sign', 'lock', 'tiles', 'publish'], [1, 2], AMBER, 'stuck after a crash'],
		['sunlight', ['tiles', 'sign', 'lock', 'publish'], null, GREEN, 'recovers alone'],
		['staged', ['stage', 'sign', 'lock', 'copy', 'publish'], null, GREEN, 'recovers alone, any storage'],
	];
	proto.forEach(([name, steps, danger, c, verdict], i) => {
		const y = 60 + i * 100;
		od.text(30, y + 32, name, { size: 21, weight: 700, color: c });
		steps.forEach((s, j) => {
			const x = 190 + j * 118;
			const col = s === 'lock' ? BLUE : s === 'sign' ? INK : PENCIL;
			od.rect(x, y + 8, 104, 40, { stroke: col, fill: s === 'lock' ? 'rgba(40,80,150,0.10)' : PAPER2, fillStyle: 'solid', strokeWidth: 1.6 });
			od.text(x + 52, y + 34, s, { anchor: 'middle', size: 17, weight: s === 'lock' || s === 'sign' ? 700 : 400, color: col });
			if (j) od.arrow(x - 14, y + 28, x - 2, y + 28, { stroke: PENCIL, strokeWidth: 1 });
		});
		if (danger) {
			const x = 190 + danger[1] * 118 - 9;
			od.line(x, y, x, y + 56, { stroke: RED, strokeWidth: 3 });
			od.text(x, y - 2, 'crash here', { anchor: 'middle', size: 14, color: RED, weight: 700 });
		}
		od.text(970, y + 34, verdict, { anchor: 'end', size: 17, color: c, weight: 700 });
	});
	od.text(30, 585, 'the lock is a compare-and-swap record of the last checkpoint ever signed for this log.', { size: 18, color: BLUE });

	// ---------------------------------------------------------------- 3. the results grid
	const gr = new Plate(1000, 560, {
		seed: 113,
		title: 'Every failure, every protocol',
		desc: 'Rows: a crash before each step, storage restored from a backup, a second instance on the same storage, a fresh bucket with a reused key. Columns: naive, tiles first, lock first, Sunlight, staged. Naive forks on a crash, a rollback, a twin and a reused key. Tiles first forks on the last three. Lock first gets stuck after a crash between lock and tiles. Sunlight and staged recover from every crash. All three lock protocols stop safely on rollback, twin and reused key. With conditional writes Sunlight gets stuck after a crash before the lock half the time; staged never does.',
	});
	const cols = ['naive', 'tiles first', 'lock first', 'sunlight', 'staged'];
	const rows = [
		['crash', ['FORK', 'safe', 'stuck', 'safe', 'safe']],
		['rollback', ['FORK', 'FORK', 'stuck', 'stuck', 'stuck']],
		['twin', ['FORK', 'FORK', 'stuck', 'stuck', 'stuck']],
		['reused key', ['FORK', 'FORK', 'stuck', 'stuck', 'stuck']],
		['crash, conditional writes', ['FORK', 'stuck', 'stuck', 'stuck', 'safe']],
	];
	const GX = 300, GW = 132, GY = 70, GH = 74;
	cols.forEach((c, j) => gr.text(GX + j * GW + GW / 2, GY - 12, c, { anchor: 'middle', size: 18, weight: 700 }));
	rows.forEach(([r, vals], i) => {
		const y = GY + i * GH;
		gr.text(GX - 16, y + 42, r, { anchor: 'end', size: 18, weight: 700 });
		vals.forEach((v, j) => {
			const c = v === 'FORK' ? RED : v === 'stuck' ? AMBER : GREEN;
			gr.rect(GX + j * GW + 4, y + 6, GW - 8, GH - 12, { stroke: c, fill: c, fillStyle: v === 'FORK' ? 'cross-hatch' : 'hachure', hachureGap: 8, strokeWidth: 1.6 });
			gr.text(GX + j * GW + GW / 2, y + 44, v, { anchor: 'middle', size: 19, weight: 700, color: INK });
		});
	});
	gr.text(30, 470, 'red: two signed histories. amber: the log stops and waits for an operator. green: it carries on.', { size: 18 });
	gr.text(30, 504, '"crash" is the worst step for each protocol; the full table is in the article.', { size: 17, color: PENCIL });
	gr.text(30, 540, 'stuck is a failure of availability. A fork is the end of the log.', { size: 20, weight: 700 });

	// ---------------------------------------------------------------- 4. staging
	const sg = new Plate(1000, 560, {
		seed: 114,
		title: 'Staging: write where nobody looks, then commit',
		desc: 'The staged protocol writes the new tiles under staging/<size>/<root>/, a private name that only this exact tree can have. Then it signs, then compare-and-swaps the lock, then copies the staged tiles into their public paths and publishes the checkpoint. If it crashes after the lock, recovery finds the staged files for the locked size and root and rolls forward. If it crashes before the lock, the staged files belong to a tree nobody committed to, and are simply ignored.',
	});
	const box = (x, y, w, t, s, c) => {
		sg.rect(x, y, w, 90, { stroke: c, fill: PAPER2, fillStyle: 'solid', strokeWidth: 2 });
		sg.text(x + w / 2, y + 36, t, { anchor: 'middle', size: 20, weight: 700, color: c });
		sg.text(x + w / 2, y + 64, s, { anchor: 'middle', size: 15, color: PENCIL });
	};
	box(30, 80, 270, 'stage', 'staging/<size>/<root>/tile/...', PENCIL);
	box(360, 80, 140, 'sign', 'checkpoint', INK);
	box(560, 80, 160, 'lock (CAS)', 'old -> new', BLUE);
	box(780, 80, 190, 'copy, publish', 'public paths', GREEN);
	sg.arrow(302, 125, 356, 125, { stroke: PENCIL, strokeWidth: 1.4 });
	sg.arrow(502, 125, 556, 125, { stroke: PENCIL, strokeWidth: 1.4 });
	sg.arrow(722, 125, 776, 125, { stroke: PENCIL, strokeWidth: 1.4 });
	sg.line(750, 60, 750, 230, { stroke: BLUE, strokeWidth: 2.4 });
	sg.text(750, 50, 'committed from here on', { anchor: 'middle', size: 18, color: BLUE, weight: 700 });
	sg.rect(30, 240, 560, 100, { stroke: PENCIL, fill: 'none', strokeWidth: 1.2 });
	sg.text(50, 274, 'crash before the lock:', { size: 19, weight: 700, color: INK });
	sg.text(50, 302, 'staged files of a tree nobody committed to.', { size: 17, color: PENCIL });
	sg.text(50, 326, 'Ignored. The next round stages under another root.', { size: 17, color: PENCIL });
	sg.rect(680, 240, 290, 100, { stroke: GREEN, fill: 'none', strokeWidth: 1.4 });
	sg.text(700, 274, 'crash after the lock:', { size: 19, weight: 700, color: GREEN });
	sg.text(700, 302, 'recovery finds staging/', { size: 17, color: GREEN });
	sg.text(700, 326, '<size>/<root>, rolls forward.', { size: 17, color: GREEN });
	sg.text(30, 420, 'public paths are only ever written with tiles of a committed tree,', { size: 19 });
	sg.text(30, 448, 'so write-once storage never refuses, and nothing beyond the lock is ever public.', { size: 19 });
	sg.text(30, 530, 'Let\'s Encrypt\'s MTC tile code has a similar step: Stage under a prefix from size and root, then Publish.', { size: 17, color: PENCIL });

	// ---------------------------------------------------------------- 5. the witness
	const wt = new Plate(1000, 520, {
		seed: 115,
		title: 'The witness remembers',
		desc: 'A tiles-first log restored from a backup. The witness cosigns checkpoints 62, 222, 312 and 595. After the restore the log publishes 322 and 593: older than what the witness cosigned, refused. Then 817, 954, 1032 and 1311: larger, but no consistency proof from 595 can exist, because the history differs. All refused. The log is dead to every client that requires this witness.',
	});
	const pts = [[62, 'ok'], [222, 'ok'], [312, 'ok'], [595, 'ok'], [322, 'old'], [593, 'old'], [817, 'fork'], [954, 'fork'], [1032, 'fork'], [1311, 'fork']];
	const WX0 = 80, WS = 88;
	wt.line(WX0 - 20, 260, WX0 + WS * 9 + 40, 260, { stroke: PENCIL, strokeWidth: 1.2 });
	pts.forEach(([n, k], i) => {
		const x = WX0 + i * WS;
		const c = k === 'ok' ? GREEN : k === 'old' ? AMBER : RED;
		wt.circle(x, 260, 44, { stroke: c, fill: c, fillStyle: k === 'ok' ? 'solid' : 'hachure', strokeWidth: 2 });
		wt.text(x, 214, String(n), { anchor: 'middle', size: 18, weight: 700, color: c });
		wt.text(x, 310, k === 'ok' ? 'cosign' : 'refuse', { anchor: 'middle', size: 15, color: c });
	});
	wt.line(WX0 + 3.5 * WS, 150, WX0 + 3.5 * WS, 360, { stroke: AMBER, strokeWidth: 2.4 });
	wt.text(WX0 + 3.5 * WS + 8, 160, 'storage restored from a backup', { size: 17, color: AMBER, weight: 700 });
	wt.text(WX0 + 4.5 * WS, 400, 'older than 595', { anchor: 'middle', size: 16, color: AMBER });
	wt.text(WX0 + 7.5 * WS, 400, 'no consistency proof from 595 exists', { anchor: 'middle', size: 16, color: RED });
	wt.text(30, 490, 'Part 05\'s witness turns a silent fork into a log that nobody can use: the failure is loud.', { size: 19, weight: 700 });

	return { '10-fork': fk, '10-orders': od, '10-grid': gr, '10-staged': sg, '10-witness': wt };
}
