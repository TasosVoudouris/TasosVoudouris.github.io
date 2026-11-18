// Hand-drawn figure toolkit for the Root of Trust series.
//
// Figures are plain SVG files drawn with rough.js (wobbly, pencil-like
// strokes) on cream "paper", with the Caveat handwriting font embedded as a
// subset (only the characters a figure uses), so they render the same
// everywhere, including inside <img>.
//
//   node scripts/figures/build.mjs            regenerate every figure
//
// Generated files go to public/images/root/. Commit them; CI does not run
// this script.
import rough from 'roughjs';
import { execFileSync } from 'node:child_process';
import { mkdtempSync, readFileSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
const FONT_DIR = join(require.resolve('@fontsource/caveat/package.json'), '..', 'files');

export const INK = '#1f1d1a';
export const RED = '#b0392b';
export const BLUE = '#2a4f86';
export const GREEN = '#2f7a4a';
export const PENCIL = '#7c766a';
export const PAPER = '#efe9d8';
export const HIGHLIGHT = 'rgba(232, 196, 72, 0.55)';

const esc = (s) =>
	String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

export class Plate {
	constructor(width, height, { seed = 7, title = '', desc = '' } = {}) {
		this.w = width;
		this.h = height;
		this.title = title;
		this.desc = desc;
		this.gen = rough.generator();
		this.seed = seed;
		this.parts = [];
		this.chars = new Set();
	}

	#opts(o = {}) {
		return {
			seed: this.seed++,
			roughness: 1.1,
			bowing: 1.2,
			stroke: INK,
			strokeWidth: 1.6,
			...o,
		};
	}

	#emit(drawable) {
		for (const p of this.gen.toPaths(drawable)) {
			const fill = p.fill && p.fill !== 'none' ? p.fill : 'none';
			this.parts.push(
				`<path d="${p.d}" stroke="${p.stroke}" stroke-width="${p.strokeWidth}" fill="${fill}" stroke-linecap="round" stroke-linejoin="round"/>`,
			);
		}
		return this;
	}

	rect(x, y, w, h, o = {}) {
		return this.#emit(this.gen.rectangle(x, y, w, h, this.#opts(o)));
	}
	line(x1, y1, x2, y2, o = {}) {
		return this.#emit(this.gen.line(x1, y1, x2, y2, this.#opts(o)));
	}
	ellipse(cx, cy, w, h, o = {}) {
		return this.#emit(this.gen.ellipse(cx, cy, w, h, this.#opts(o)));
	}
	circle(cx, cy, d, o = {}) {
		return this.#emit(this.gen.circle(cx, cy, d, this.#opts(o)));
	}
	poly(points, o = {}) {
		return this.#emit(this.gen.polygon(points, this.#opts(o)));
	}
	curve(points, o = {}) {
		return this.#emit(this.gen.curve(points, this.#opts(o)));
	}
	svgPath(d, o = {}) {
		return this.#emit(this.gen.path(d, this.#opts(o)));
	}

	/** Straight arrow with a hand-drawn head. */
	arrow(x1, y1, x2, y2, o = {}) {
		this.line(x1, y1, x2, y2, o);
		const a = Math.atan2(y2 - y1, x2 - x1);
		const len = o.head ?? 13;
		for (const s of [-1, 1]) {
			const b = a + Math.PI + s * 0.45;
			this.line(x2, y2, x2 + len * Math.cos(b), y2 + len * Math.sin(b), { ...o, roughness: 0.6 });
		}
		return this;
	}

	/** Curved arrow through a control point. */
	curvedArrow(x1, y1, cx, cy, x2, y2, o = {}) {
		this.curve(
			[
				[x1, y1],
				[cx, cy],
				[x2, y2],
			],
			o,
		);
		const a = Math.atan2(y2 - cy, x2 - cx);
		const len = o.head ?? 13;
		for (const s of [-1, 1]) {
			const b = a + Math.PI + s * 0.45;
			this.line(x2, y2, x2 + len * Math.cos(b), y2 + len * Math.sin(b), { ...o, roughness: 0.6 });
		}
		return this;
	}

	/** Translucent marker stroke behind text or an area. */
	highlight(x, y, w, h, color = HIGHLIGHT) {
		return this.#emit(
			this.gen.rectangle(x, y, w, h, this.#opts({ stroke: 'none', fill: color, fillStyle: 'solid', roughness: 1.6 })),
		);
	}

	/** Hatched fill, like shading with a pencil. */
	hatch(x, y, w, h, color = PENCIL) {
		return this.#emit(
			this.gen.rectangle(x, y, w, h, this.#opts({ stroke: 'none', fill: color, fillStyle: 'hachure', hachureGap: 7, fillWeight: 1 })),
		);
	}

	/**
	 * Handwritten text. `lines` may be a string with \n.
	 * o: size, color, anchor ('start'|'middle'|'end'), weight (400|700), rotate (deg), lh (line height factor)
	 */
	text(x, y, lines, o = {}) {
		const size = o.size ?? 26;
		const color = o.color ?? INK;
		const anchor = o.anchor ?? 'start';
		const weight = o.weight ?? 400;
		const lh = o.lh ?? 1.12;
		const rot = o.rotate ? ` transform="rotate(${o.rotate} ${x} ${y})"` : '';
		const rows = String(lines).split('\n');
		for (const r of rows) for (const c of r) this.chars.add(c);
		const tspans = rows
			.map((r, i) => `<tspan x="${x}" dy="${i === 0 ? 0 : size * lh}">${esc(r)}</tspan>`)
			.join('');
		this.parts.push(
			`<text x="${x}" y="${y}" font-family="CaveatQ" font-size="${size}" font-weight="${weight}" fill="${color}" text-anchor="${anchor}"${rot}>${tspans}</text>`,
		);
		return this;
	}

	#font(weight) {
		const chars = [...this.chars].join('') + ' ';
		const dir = mkdtempSync(join(tmpdir(), 'qfont-'));
		const out = join(dir, 'sub.woff2');
		writeFileSync(join(dir, 'chars.txt'), chars);
		execFileSync('pyftsubset', [
			join(FONT_DIR, `caveat-latin-${weight}-normal.woff2`),
			`--text-file=${join(dir, 'chars.txt')}`,
			'--flavor=woff2',
			`--output-file=${out}`,
		]);
		return readFileSync(out).toString('base64');
	}

	toSVG() {
		const usesBold = this.parts.some((p) => p.includes('font-weight="700"'));
		const faces = [
			`@font-face{font-family:CaveatQ;font-weight:400;src:url(data:font/woff2;base64,${this.#font(400)}) format("woff2")}`,
			usesBold
				? `@font-face{font-family:CaveatQ;font-weight:700;src:url(data:font/woff2;base64,${this.#font(700)}) format("woff2")}`
				: '',
		].join('');
		return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${this.w} ${this.h}" width="${this.w}" height="${this.h}" role="img" aria-labelledby="t d">
<title id="t">${esc(this.title)}</title>
<desc id="d">${esc(this.desc)}</desc>
<style>${faces}</style>
<rect width="100%" height="100%" fill="${PAPER}"/>
${this.parts.join('\n')}
</svg>
`;
	}
}
