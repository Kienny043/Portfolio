import { formatDate } from '../lib/format'
import { Reveal, Section } from './ui'

// Renders nothing until there is at least one published post (App only mounts it then).
export default function Blog({ number, posts }) {
  return (
    <Section id="blog" number={number} title="Blog">
      <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
        {posts.map((post, i) => (
          <Reveal key={post.post_id} delay={i * 90} className="h-full">
          <article
            className="flex h-full flex-col rounded-3xl border border-ink/10 bg-white p-6 transition hover:-translate-y-1 hover:shadow-lg"
          >
            {post.published_at && (
              <p className="text-xs font-semibold uppercase tracking-widest text-accent2">
                {formatDate(post.published_at)}
              </p>
            )}
            <h3 className="mt-2 text-xl font-semibold leading-snug">{post.title}</h3>
            {post.excerpt && <p className="mt-3 leading-relaxed text-ink/75">{post.excerpt}</p>}
          </article>
          </Reveal>
        ))}
      </div>
    </Section>
  )
}
