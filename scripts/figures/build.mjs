// Regenerate all Root of Trust figures:  node scripts/figures/build.mjs
import { mkdirSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { part00 } from './part00.mjs';
import { part01 } from './part01.mjs';
import { part02 } from './part02.mjs';
import { part03 } from './part03.mjs';
import { part04 } from './part04.mjs';
import { part05 } from './part05.mjs';
import { part06 } from './part06.mjs';
import { part07 } from './part07.mjs';
import { part08 } from './part08.mjs';
import { part09 } from './part09.mjs';
import { part10 } from './part10.mjs';
import { part11 } from './part11.mjs';

const OUT = join(process.cwd(), 'public', 'images', 'root');
mkdirSync(OUT, { recursive: true });

for (const [name, plate] of Object.entries({ ...part00(), ...part01(), ...part02(), ...part03(), ...part04(), ...part05(), ...part06(), ...part07(), ...part08(), ...part09(), ...part10(), ...part11() })) {
	const svg = plate.toSVG();
	writeFileSync(join(OUT, `${name}.svg`), svg);
	console.log(`wrote public/images/root/${name}.svg (${(svg.length / 1024).toFixed(1)} KiB)`);
}
