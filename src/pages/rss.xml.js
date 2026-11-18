import { getCollection } from 'astro:content';
import rss from '@astrojs/rss';
import { SITE_DESCRIPTION, SITE_TITLE } from '../consts';

export async function GET(context) {
	const posts = (await getCollection('blog'))
		.filter((post) => !post.data.draft)
		.sort(
			(a, b) =>
				b.data.pubDate.valueOf() - a.data.pubDate.valueOf() ||
				b.id.localeCompare(a.id),
		);

	const rootParts = (await getCollection('root')).filter((p) => !p.data.draft);
	const items = [
		...posts.map((post) => ({
			title: post.data.title,
			description: post.data.description,
			pubDate: post.data.pubDate,
			link: `/blog/${post.id}/`,
		})),
		...rootParts.map((p) => ({
			title: `Root of Trust ${String(p.data.part).padStart(2, '0')}: ${p.data.title}`,
			description: p.data.description,
			pubDate: p.data.pubDate,
			link: `/root/${p.id}/`,
		})),
	].sort((a, b) => b.pubDate.valueOf() - a.pubDate.valueOf());

	return rss({
		title: SITE_TITLE,
		description: SITE_DESCRIPTION,
		site: context.site,
		items,
	});
}
