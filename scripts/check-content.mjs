import fs from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { createMarkdownProcessor } from '@astrojs/markdown-remark';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';

const root = process.cwd();
const blogDir = path.join(root, 'src', 'content', 'blog');

function read(rel) {
  return fs.readFileSync(path.join(root, rel), 'utf8');
}

function extractConstArray(source, name) {
  const match = source.match(new RegExp(`export\\s+const\\s+${name}\\s*=\\s*\\[([\\s\\S]*?)\\]\\s+as\\s+const`));
  if (!match) throw new Error(`Could not read ${name}`);
  return [...match[1].matchAll(/'([^']+)'/g)].map((m) => m[1]);
}

const allowedSeries = new Set(extractConstArray(read('src/data/series.ts'), 'SERIES_NAMES'));
const allowedTopics = new Set(extractConstArray(read('src/data/topics.ts'), 'TOPIC_NAMES'));
const allowedDifficulty = new Set(['Introductory', 'Intermediate', 'Advanced']);
const allowedStatus = new Set(['Reviewed', 'Validated', 'Reference', 'Research Note', 'Experimental']);

function walk(dir) {
  return fs.readdirSync(dir, { withFileTypes: true }).flatMap((entry) => {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) return walk(full);
    return /\.(md|mdx)$/i.test(entry.name) ? [full] : [];
  });
}

function frontmatterOf(text) {
  if (!text.startsWith('---')) return null;
  const end = text.indexOf('\n---', 3);
  if (end < 0) return null;
  return { fm: text.slice(3, end), body: text.slice(end + 4).trim() };
}

function scalar(fm, key) {
  const m = fm.match(new RegExp(`^${key}:\\s*(.+?)\\s*$`, 'm'));
  if (!m) return undefined;
  return m[1].trim().replace(/^['"]|['"]$/g, '');
}

function list(fm, key) {
  const lines = fm.split(/\r?\n/);
  const start = lines.findIndex((line) => new RegExp(`^${key}:\\s*$`).test(line));
  if (start < 0) return [];
  const out = [];
  let seenValue = false;
  for (let i = start + 1; i < lines.length; i += 1) {
    if (!lines[i].trim() && !seenValue) continue;
    const m = lines[i].match(/^\s*-\s*(.+?)\s*$/);
    if (!m) break;
    seenValue = true;
    out.push(m[1].trim().replace(/^['"]|['"]$/g, ''));
  }
  return out;
}

function withoutFencedCode(body) {
  return body.replace(/```[\s\S]*?```/g, '').replace(/~~~[\s\S]*?~~~/g, '');
}

function withoutInlineCode(line) {
  // Remove inline-code spans before validating prose/math delimiters.
  // This is intentionally conservative: math-like text inside code is allowed.
  return line.replace(/(`+)(.*?)\1/g, '');
}

function validateMathDelimiters(rel, body, errors) {
  const prose = withoutFencedCode(body);
  const lines = prose.split(/\r?\n/);

  for (let i = 0; i < lines.length; i += 1) {
    const line = lines[i];
    const trimmed = line.trim();

    // remark-math on this site supports $...$ and $$...$$. The TeX-style
    // Markdown delimiters \(...\) and \[...\] are not recognized here
    // and would be rendered literally on the site.
    if (trimmed === '\\[' || trimmed === '\\]') {
      errors.push(`${rel}:${i + 1}: unsupported display-math delimiter "${trimmed}"; use $$`);
    }

    const visible = withoutInlineCode(line);
    if (visible.includes('\\(') || visible.includes('\\)')) {
      errors.push(`${rel}:${i + 1}: unsupported inline-math delimiter \(...\); use $...$`);
    }
  }

  const standaloneDollarLines = lines.filter((line) => line.trim() === '$$').length;
  if (standaloneDollarLines % 2 !== 0) {
    errors.push(`${rel}: unbalanced standalone $$ display-math delimiters`);
  }
}

function localImageTarget(asset) {
  const clean = asset.split('#')[0].split('?')[0];
  return {
    asset: clean,
    target: path.join(root, 'public', clean.replace(/^\//, '')),
  };
}


const errors = [];
const seriesOrders = new Map();
const ordersBySeries = new Map();
const files = walk(blogDir);
const blogSlugs = new Set(
  files.map((file) => path.relative(blogDir, file).replaceAll('\\', '/').replace(/\.(md|mdx)$/i, '')),
);
const titles = new Map();
const markdownProcessor = await createMarkdownProcessor({
  remarkPlugins: [remarkMath],
  rehypePlugins: [rehypeKatex],
  syntaxHighlight: false,
});

for (const file of files) {
  const rel = path.relative(root, file).replaceAll('\\', '/');
  const text = fs.readFileSync(file, 'utf8');
  const parsed = frontmatterOf(text);
  if (!parsed) {
    errors.push(`${rel}: missing or malformed frontmatter`);
    continue;
  }
  const { fm, body } = parsed;

  for (const key of ['title', 'description', 'pubDate']) {
    if (!scalar(fm, key)) errors.push(`${rel}: missing ${key}`);
  }
  if (!body) errors.push(`${rel}: empty article body`);

  const pubDateRaw = scalar(fm, 'pubDate');
  const updatedDateRaw = scalar(fm, 'updatedDate');
  if (pubDateRaw && Number.isNaN(Date.parse(pubDateRaw))) errors.push(`${rel}: invalid pubDate "${pubDateRaw}"`);
  if (updatedDateRaw && Number.isNaN(Date.parse(updatedDateRaw))) errors.push(`${rel}: invalid updatedDate "${updatedDateRaw}"`);
  if (pubDateRaw && updatedDateRaw && !Number.isNaN(Date.parse(pubDateRaw)) && !Number.isNaN(Date.parse(updatedDateRaw)) && Date.parse(updatedDateRaw) < Date.parse(pubDateRaw)) {
    errors.push(`${rel}: updatedDate precedes pubDate`);
  }

  const title = scalar(fm, 'title');
  if (title) {
    if (titles.has(title)) errors.push(`${rel}: duplicate title "${title}" (also ${titles.get(title)})`);
    else titles.set(title, rel);
  }

  const difficulty = scalar(fm, 'difficulty') ?? 'Introductory';
  if (!allowedDifficulty.has(difficulty)) errors.push(`${rel}: invalid difficulty "${difficulty}"`);
  const status = scalar(fm, 'status');
  if (status && !allowedStatus.has(status)) errors.push(`${rel}: invalid status "${status}"`);

  const topics = list(fm, 'topics');
  if (!topics.length) errors.push(`${rel}: topics must contain at least one value`);
  for (const topic of topics) {
    if (!allowedTopics.has(topic)) errors.push(`${rel}: invalid topic "${topic}"`);
  }

  const series = scalar(fm, 'series');
  const orderRaw = scalar(fm, 'seriesOrder');
  if (series && !allowedSeries.has(series)) errors.push(`${rel}: invalid series "${series}"`);
  if (series && orderRaw === undefined) errors.push(`${rel}: has series but no seriesOrder`);
  if (!series && orderRaw !== undefined) errors.push(`${rel}: has seriesOrder but no series`);
  if (series && orderRaw !== undefined && allowedSeries.has(series)) {
    const order = Number(orderRaw);
    if (!Number.isInteger(order) || order < 1) {
      errors.push(`${rel}: invalid seriesOrder "${orderRaw}" (series positions are one-based)`);
    } else {
      const key = `${series}::${order}`;
      if (seriesOrders.has(key)) {
        errors.push(`${rel}: duplicate ${series} seriesOrder ${order} (also ${seriesOrders.get(key)})`);
      } else {
        seriesOrders.set(key, rel);
        if (!ordersBySeries.has(series)) ordersBySeries.set(series, []);
        ordersBySeries.get(series).push(order);
      }
    }
  }

  const sourcePath = scalar(fm, 'sourcePath');
  if (sourcePath) {
    const target = path.join(root, sourcePath);
    if (!fs.existsSync(target)) errors.push(`${rel}: missing sourcePath target "${sourcePath}"`);
  }

  const codeFenceCount = (body.match(/^\s{0,3}```/gm) ?? []).length;
  if (codeFenceCount % 2 !== 0) errors.push(`${rel}: unbalanced triple-backtick code fences`);

  validateMathDelimiters(rel, body, errors);

  const visibleBody = withoutFencedCode(body);

  // Markdown local images.
  for (const match of visibleBody.matchAll(/!?\[[^\]]*\]\((\/images\/[^)\s]+)(?:\s+['"][^'"]*['"])?\)/g)) {
    const { asset, target } = localImageTarget(match[1]);
    if (!fs.existsSync(target)) errors.push(`${rel}: missing local image asset "${asset}"`);
  }

  // Raw HTML local images, which are common in older imported notes.
  for (const match of visibleBody.matchAll(/<img\b[^>]*\bsrc\s*=\s*['"](\/images\/[^'"]+)['"][^>]*>/gi)) {
    const { asset, target } = localImageTarget(match[1]);
    if (!fs.existsSync(target)) errors.push(`${rel}: missing local HTML image asset "${asset}"`);
  }

  // Absolute article links must resolve to an existing content slug.
  for (const match of visibleBody.matchAll(/\]\(\/blog\/([^/#?\s)]+)\/?(?:[?#][^)]*)?\)/g)) {
    const slug = match[1];
    if (!blogSlugs.has(slug)) errors.push(`${rel}: broken internal blog link "/blog/${slug}/"`);
  }

  // Render with the same math plugins as Astro and verify local anchor links against actual generated IDs.
  try {
    const rendered = await markdownProcessor.render(body, { fileURL: pathToFileURL(file) });
    const ids = new Set([...rendered.code.matchAll(/\bid=["']([^"']+)["']/g)].map((m) => m[1]));
    for (const match of rendered.code.matchAll(/\bhref=["']#([^"']+)["']/g)) {
      let anchor = match[1];
      try { anchor = decodeURIComponent(anchor); } catch { /* keep the raw anchor */ }
      if (!ids.has(anchor)) errors.push(`${rel}: broken local anchor "#${anchor}"`);
    }
  } catch (error) {
    errors.push(`${rel}: Markdown rendering failed during anchor validation: ${error?.message ?? error}`);
  }
}

for (const [series, orders] of ordersBySeries) {
  const sorted = [...orders].sort((a, b) => a - b);
  for (let i = 0; i < sorted.length; i += 1) {
    const expected = i + 1;
    if (sorted[i] !== expected) {
      errors.push(`${series}: non-contiguous seriesOrder sequence; expected ${expected} but found ${sorted[i]}`);
      break;
    }
  }
}

if (errors.length) {
  console.error('\nCryptoCave content preflight failed:\n');
  for (const error of errors) console.error(`  - ${error}`);
  console.error('\nThis can indicate stale files from an older CryptoCave extraction or a broken new content import.');
  console.error('Use a NEW/EMPTY working directory for master upgrades and fix the reported canonical source instead of weakening the schema.\n');
  process.exit(1);
}

console.log(`CryptoCave content preflight: OK (${files.length} articles, ${allowedSeries.size} series, ${allowedTopics.size} topics).`);
