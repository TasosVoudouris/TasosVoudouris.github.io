import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

import { TOPIC_NAMES } from './data/topics';

const blog = defineCollection({
	loader: glob({
		base: './src/content/blog',
		pattern: '**/*.{md,mdx}',
	}),

	schema: z.object({
		title: z.string(),

		description: z.string(),

		pubDate: z.coerce.date(),

		updatedDate: z.coerce.date().optional(),

		heroImage: z.any().optional(),

		category: z.enum(TOPIC_NAMES),

		tags: z.array(z.string()).default([]),

		difficulty: z
			.enum([
				'Introductory',
				'Intermediate',
				'Advanced',
			])
			.default('Introductory'),

		series: z.string().optional(),

		draft: z.boolean().default(false),
	}),
});

export const collections = {
	blog,
};