// Regenerate all Root of Trust figures:  node scripts/figures/build.mjs
import { mkdirSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { part00 } from './part00.mjs';
import { part01 } from './part01.mjs';

const OUT = join(process.cwd(), 'public', 'images', 'root');
mkdirSync(OUT, { recursive: true });

for (const [name, plate] of Object.entries({ ...part00(), ...part01() })) {
	const svg = plate.toSVG();
	writeFileSync(join(OUT, `${name}.svg`), svg);
	console.log(`wrote public/images/root/${name}.svg (${(svg.length / 1024).toFixed(1)} KiB)`);
}
