// Figures for Root of Trust, part 05: "Notes, checkpoints, witnesses"
import { Plate, INK, RED, BLUE, GREEN, PENCIL } from './sketch.mjs';

const AMBER = '#b8741a';
const PAPER2 = '#fbf8ef';

function box(p, x, y, w, h, label, { color = INK, size = 22, fill = PAPER2, weight = 700, sub } = {}) {
	p.rect(x, y, w, h, { stroke: color, fill, fillStyle: 'solid', strokeWidth: 1.6 });
	p.text(x + w / 2, y + (sub ? h / 2 - 4 : h / 2 + size * 0.33), label, { anchor: 'middle', size, color, weight });
	if (sub) p.text(x + w / 2, y + h / 2 + 20, sub, { anchor: 'middle', size: size - 5, color: PENCIL, lh: 1.05 });
}

export function part05() {
	// ---------------------------------------------------------------- 1. anatomy of a cosigned checkpoint
	const an = new Plate(1000, 640, {
		seed: 61,
		title: 'Anatomy of a cosigned checkpoint',
		desc: 'A checkpoint is a signed note. Its text has three lines: the origin naming the log, the tree size, and the root hash in base64. A blank line separates it from the signature lines. Each signature line is an em dash, the key name, and base64 of a 4-byte key ID followed by the signature. A witness cosignature line also carries an 8-byte timestamp before its signature.',
	});
	an.rect(40, 40, 600, 150, { stroke: BLUE, fill: '#eef1f8', fillStyle: 'solid', strokeWidth: 1.8 });
	const mono = (x, y, s, c = INK, size = 22) => an.text(x, y, s, { size, color: c, weight: 700 });
	mono(60, 80, 'example.com/log');
	mono(60, 120, '1000');
	mono(60, 160, 'AcWjVY4EmQlPJ4tm380spGWTDrMo9Vvl...=');
	an.text(670, 80, 'origin: which log', { size: 21, color: BLUE });
	an.text(670, 120, 'tree size, in decimal', { size: 21, color: BLUE });
	an.text(670, 160, 'root hash, base64', { size: 21, color: BLUE });
	an.text(60, 222, '(blank line: the text ends at the last one)', { size: 19, color: PENCIL });

	an.rect(40, 245, 600, 50, { stroke: GREEN, fill: '#eef3ee', fillStyle: 'solid', strokeWidth: 1.6 });
	mono(60, 278, '— example.com/log  sKX2TK4E...=', GREEN);
	an.text(670, 278, 'the log\'s own signature', { size: 21, color: GREEN });
	for (let i = 0; i < 3; i++) {
		an.rect(40, 310 + i * 60, 600, 50, { stroke: AMBER, fill: '#f6efe2', fillStyle: 'solid', strokeWidth: 1.6 });
		mono(60, 343 + i * 60, `— witness-${'abc'[i]}.example  ${['cEDLggAA', 'oWzQmAAA', 'UUfwFwAA'][i]}...=`, AMBER);
	}
	an.text(670, 370, 'cosignatures from\nthree witnesses', { size: 21, color: AMBER });

	an.text(40, 530, 'inside one cosignature value (76 bytes, base64):', { size: 22, weight: 700 });
	const parts = [['key ID', '4 B', 160, PENCIL], ['timestamp', '8 B', 200, AMBER], ['Ed25519 signature over "cosignature/v1", "time T", checkpoint', '64 B', 540, RED]];
	let x = 40;
	for (const [label, n, w, c] of parts) {
		an.rect(x, 548, w, 56, { stroke: c, fill: PAPER2, fillStyle: 'solid', strokeWidth: 1.6 });
		an.text(x + w / 2, 572, label, { anchor: 'middle', size: 18, color: c, weight: 700 });
		an.text(x + w / 2, 596, n, { anchor: 'middle', size: 18, color: PENCIL });
		x += w + 8;
	}

	// ---------------------------------------------------------------- 2. the witness protocol
	const wf = new Plate(1000, 600, {
		seed: 62,
		title: 'How a witness cosigns',
		desc: 'The log sends add-checkpoint: the old size the witness last cosigned, a consistency proof from it, and the new checkpoint. The witness checks the log signature, the old size against its stored state, and the proof, then stores the new size and root and returns a cosignature. The log publishes the checkpoint with its cosignatures; a client accepts it only with enough of them.',
	});
	box(wf, 40, 80, 200, 90, 'log', { color: BLUE, size: 28 });
	box(wf, 560, 60, 380, 300, '', { color: AMBER });
	wf.text(750, 98, 'witness', { anchor: 'middle', size: 28, weight: 700, color: AMBER });
	wf.text(590, 140, 'stores, per log: (size, root)\nof the last checkpoint it cosigned', { size: 20, color: PENCIL });
	const checks = ['signed by the log?   else 403', 'old size = my size?   else 409', 'proof: my root -> new root?   else 422', 'save new (size, root), then sign'];
	checks.forEach((c, i) => wf.text(590, 214 + i * 36, `${i + 1}. ${c}`, { size: 20, color: i === 3 ? GREEN : INK }));
	wf.arrow(244, 110, 554, 110, { stroke: BLUE, strokeWidth: 1.8 });
	wf.text(260, 96, 'old 1000 + proof + checkpoint 1500', { size: 19, color: BLUE });
	wf.arrow(554, 300, 244, 150, { stroke: AMBER, strokeWidth: 1.8 });
	wf.text(300, 250, 'cosignature line', { size: 20, color: AMBER });
	box(wf, 40, 420, 300, 110, 'published checkpoint', { color: GREEN, size: 22, sub: 'log signature +\nwitness cosignatures' });
	wf.arrow(140, 172, 140, 416, { stroke: GREEN, strokeWidth: 1.6 });
	box(wf, 560, 430, 380, 100, 'client', { color: INK, size: 26, sub: 'log key + k of n witness keys' });
	wf.arrow(344, 475, 556, 478, { stroke: GREEN, strokeWidth: 1.6 });
	wf.text(40, 580, 'a witness keeps one number and one hash per log, and never signs two histories.', { size: 21, weight: 700 });

	// ---------------------------------------------------------------- 3. the fork refused
	const fk = new Plate(1000, 520, {
		seed: 63,
		title: 'Why a fork cannot be witnessed',
		desc: 'Main branch and fork share the first 1000 entries; the fork inserts a rogue certificate after them. Every witness already cosigned main at 1500. A fork checkpoint of the same size has a different root, which the witness refuses (422). A bigger fork has no consistency proof from main at 1500 (422). Only a witness that never saw main can be fooled.',
	});
	const Y = 220, X0 = 60, sc = 0.42;
	fk.line(X0, Y, X0 + 1000 * sc, Y, { stroke: INK, strokeWidth: 3 });
	fk.text(X0, Y - 18, 'shared: entries 0 .. 999', { size: 20 });
	const bx = X0 + 1000 * sc;
	fk.line(bx, Y, bx + 500 * sc, Y - 80, { stroke: GREEN, strokeWidth: 3 });
	fk.line(bx + 500 * sc, Y - 80, bx + 800 * sc, Y - 80, { stroke: GREEN, strokeWidth: 3, strokeLineDash: [8, 6] });
	fk.text(bx + 520 * sc, Y - 96, 'main: cosigned at 1500 by a, b, c', { size: 20, color: GREEN, weight: 700 });
	fk.line(bx, Y, bx + 500 * sc, Y + 80, { stroke: RED, strokeWidth: 3 });
	fk.line(bx + 500 * sc, Y + 80, bx + 800 * sc, Y + 80, { stroke: RED, strokeWidth: 3 });
	fk.circle(bx + 14, Y + 6, 16, { stroke: RED, fill: RED, fillStyle: 'solid' });
	fk.text(bx + 30, Y + 44, 'rogue cert', { size: 19, color: RED });
	fk.text(bx + 520 * sc, Y + 112, 'fork', { size: 21, color: RED, weight: 700 });
	fk.circle(bx + 500 * sc, Y + 80, 14, { stroke: RED });
	fk.circle(bx + 800 * sc, Y + 80, 14, { stroke: RED });
	fk.text(bx + 500 * sc - 50, Y + 150, 'fork at 1500:\nsame size, other root\n-> 422', { anchor: 'middle', size: 19, color: RED });
	fk.text(bx + 800 * sc + 60, Y + 150, 'fork at 1800:\nno proof from main\n-> 422', { anchor: 'middle', size: 19, color: RED });
	fk.text(40, 470, 'once a witness has seen one branch, it can only ever sign that branch\'s future.', { size: 22, weight: 700 });
	fk.text(40, 504, 'the attack needs witnesses that never saw it: partition them, or own them.', { size: 21, color: PENCIL });

	// ---------------------------------------------------------------- 4. quorum
	const q = new Plate(1000, 560, {
		seed: 64,
		title: 'How many cosignatures stop a fork',
		desc: 'With n = 5 witnesses, f compromised and a client requiring k cosignatures: two conflicting checkpoints can both reach k exactly when 2k is at most n + f. Any two sets of k witnesses overlap in at least 2k - n witnesses; if that exceeds f, an honest witness is in both and would have refused one.',
	});
	q.text(40, 50, 'n = 5 witnesses.  fork possible?', { size: 25, weight: 700 });
	const CX = 210, CY = 110, CW = 110, CH = 64;
	for (let k = 1; k <= 5; k++) q.text(CX + (k - 1) * CW + CW / 2, CY - 14, `k = ${k}`, { anchor: 'middle', size: 21, weight: 700 });
	for (let f = 0; f <= 3; f++) {
		q.text(CX - 20, CY + f * CH + 40, `f = ${f} compromised`, { anchor: 'end', size: 20 });
		for (let k = 1; k <= 5; k++) {
			const fork = 2 * k <= 5 + f;
			const c = fork ? RED : GREEN;
			q.rect(CX + (k - 1) * CW + 4, CY + f * CH + 4, CW - 8, CH - 8, { stroke: c, fill: c, fillStyle: 'hachure', hachureGap: 8, strokeWidth: 1.4 });
			q.text(CX + (k - 1) * CW + CW / 2, CY + f * CH + 42, fork ? 'fork' : 'safe', { anchor: 'middle', size: 21, weight: 700, color: c });
		}
	}
	q.text(40, 410, 'two quorums of k overlap in at least 2k - n witnesses.', { size: 22 });
	q.text(40, 444, 'if 2k - n > f, the overlap holds an honest witness, who signs only one branch.', { size: 22 });
	q.text(40, 486, 'safe  <=>  k > (n + f) / 2', { size: 26, weight: 700, color: GREEN });
	q.text(40, 524, 'but k = n means one witness offline blocks every client: pick k with spare.', { size: 20, color: PENCIL });

	// ---------------------------------------------------------------- 5. freshness
	const fr = new Plate(1000, 420, {
		seed: 65,
		title: 'Timestamps stop a frozen view',
		desc: 'A log can keep showing a victim an old checkpoint that was honestly cosigned a month ago, hiding everything logged since. Because each cosignature carries the time the witness signed, a client that requires cosignatures younger than a day rejects the frozen checkpoint.',
	});
	const T0 = 70, T1 = 930, LY = 190;
	fr.line(T0, LY, T1, LY, { stroke: INK, strokeWidth: 2 });
	fr.arrow(T1 - 10, LY, T1 + 20, LY, { stroke: INK, strokeWidth: 2 });
	fr.circle(T0 + 40, LY, 16, { stroke: AMBER, fill: AMBER, fillStyle: 'solid' });
	fr.text(T0 + 40, LY - 64, 'checkpoint cosigned\n(time = day 0)', { anchor: 'middle', size: 20, color: AMBER });
	fr.highlight(T0 + 60, LY - 12, 700, 24, 'rgba(198, 52, 43, 0.12)');
	fr.text(T0 + 400, LY + 50, 'the log keeps serving it to one victim; new entries stay hidden', { anchor: 'middle', size: 20, color: RED });
	fr.circle(T0 + 790, LY, 16, { stroke: INK, fill: INK, fillStyle: 'solid' });
	fr.text(T0 + 790, LY - 64, 'day 30:\nvictim checks', { anchor: 'middle', size: 20 });
	fr.text(70, 330, 'no age limit:  ACCEPT, the victim sees a month-old world.', { size: 22, color: RED });
	fr.text(70, 370, 'cosignatures must be < 1 day old:  REJECT, the freeze is visible.', { size: 22, color: GREEN, weight: 700 });

	return {
		'05-anatomy': an,
		'05-witness-flow': wf,
		'05-fork-refused': fk,
		'05-quorum': q,
		'05-freshness': fr,
	};
}
