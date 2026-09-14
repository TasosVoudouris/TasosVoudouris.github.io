import type { CollectionEntry } from 'astro:content';

export type BlogEntry = CollectionEntry<'blog'>;

export function sortNewest(posts: BlogEntry[]): BlogEntry[] {
	return [...posts].sort(
		(a, b) =>
			b.data.pubDate.valueOf() - a.data.pubDate.valueOf() ||
			b.id.localeCompare(a.id),
	);
}

export function sortSeries(posts: BlogEntry[]): BlogEntry[] {
	return [...posts].sort(
		(a, b) =>
			(a.data.seriesOrder ?? Number.MAX_SAFE_INTEGER) -
				(b.data.seriesOrder ?? Number.MAX_SAFE_INTEGER) ||
			a.id.localeCompare(b.id),
	);
}
