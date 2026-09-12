# CryptoCave

CryptoCave is a static Astro site for cryptography notes, articles, implementations, experiments, and research-oriented material.

Production site: `https://tasosvoudouris.github.io`

Source repository: `https://github.com/TasosVoudouris/TasosVoudouris.github.io`

## Requirements

- Node.js 24 is recommended for local development and matches the GitHub Pages workflow.
- Node.js 22.12+ is also accepted by the project dependencies.
- npm is used through `package-lock.json`.

## Clean local setup

From the project root:

```bash
npm ci
npm run dev
```

Astro will normally start the local site at:

```text
http://localhost:4321
```

## Production validation

Before pushing changes, run:

```bash
npm run build
npm run preview
```

The production build is written to `dist/`.

## GitHub Pages

Deployment is handled by `.github/workflows/deploy.yml` whenever `main` is pushed.

This repository is the special GitHub Pages user repository `TasosVoudouris.github.io`, so the site is deployed at the domain root. `astro.config.mjs` therefore sets:

```js
site: 'https://tasosvoudouris.github.io'
```

and intentionally does **not** set an Astro `base` path.

In GitHub repository settings, Pages should use **GitHub Actions** as its source.

## Content

Articles live in:

```text
src/content/blog/
```

The schema is defined in `src/content.config.ts`. Published indexes, topic pages, tag pages, RSS, and article routes exclude posts with:

```yaml
draft: true
```

Article diagrams referenced as `/images/blog/...` live in:

```text
public/images/blog/
```

## Useful commands

```bash
npm run dev      # local development server
npm run build    # production build
npm run preview  # preview the production build locally
npm run astro -- --help
```
