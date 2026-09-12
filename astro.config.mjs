// @ts-check

import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';

import mdx from '@astrojs/mdx';
import sitemap from '@astrojs/sitemap';

import { unified } from '@astrojs/markdown-remark';
import { defineConfig, fontProviders } from 'astro/config';

// https://astro.build/config
export default defineConfig({
	// This is a user/organization GitHub Pages repository
	// (TasosVoudouris.github.io), so it is deployed at the domain root
	// and does not need a `base` path.
	site: 'https://tasosvoudouris.github.io',

	markdown: {
		processor: unified({
			remarkPlugins: [remarkMath],
			rehypePlugins: [rehypeKatex],
		}),
	},

	integrations: [mdx(), sitemap()],

	fonts: [
		{
			provider: fontProviders.local(),
			name: 'Atkinson',
			cssVariable: '--font-atkinson',
			fallbacks: ['sans-serif'],
			options: {
				variants: [
					{
						src: ['./src/assets/fonts/atkinson-regular.woff'],
						weight: 400,
						style: 'normal',
						display: 'swap',
					},
					{
						src: ['./src/assets/fonts/atkinson-bold.woff'],
						weight: 700,
						style: 'normal',
						display: 'swap',
					},
				],
			},
		},
	],
});
