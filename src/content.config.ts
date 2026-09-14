import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

import { TOPIC_NAMES } from './data/topics';
import { SERIES_NAMES } from './data/series';

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

		topics: z.array(z.enum(TOPIC_NAMES)).min(1),
		tags: z.array(z.string()).default([]),

		difficulty: z
			.enum(['Introductory', 'Intermediate', 'Advanced'])
			.default('Introductory'),

		status: z.enum(['Reviewed', 'Validated', 'Reference', 'Research Note', 'Experimental']).optional(),

		series: z.enum(SERIES_NAMES).optional(),
		seriesOrder: z.number().int().nonnegative().optional(),

		sourcePath: z.string().optional(),

		draft: z.boolean().default(false),
	}),
});

export const collections = {
	blog,
};
