import { formatDate } from '../lib/format'
import { LoadError, Reveal, Section, Skeleton } from './ui'

// Renders nothing once we know there are zero published posts. While loading or
// on error, App still mounts this (see showBlog in App.jsx) so a skeleton/error
// can show instead of the section just popping in with no warning.
export default function Blog({ number, blog }) {
  if (blog.status === 'success' && blog.data.length === 0) return null

  return (
    <Section id="blog" number={number} title="Blog">
      {blog.status === 'loading' && (
        <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
          {[0, 1, 2].map((i) => (
            <Skeleton key={i} className="h-48" />
          ))}
        </div>
      )}
      {blog.status === 'error' && <LoadError what="blog posts" />}
      {blog.status === 'success' && (
        <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
          {blog.data.map((post, i) => (
            <Reveal key={post.post_id} delay={i * 90} className="h-full">
              <article className="flex h-full flex-col rounded-3xl border border-ink/10 bg-white p-6 transition hover:-translate-y-1 hover:shadow-lg">
                {post.published_at && (
                  <p className="text-xs font-semibold uppercase tracking-widest text-accent2">
                    {formatDate(post.published_at)}
                  </p>
                )}
                <h3 className="mt-2 break-words text-xl font-semibold leading-snug">
                  {post.title}
                </h3>
                {post.excerpt && (
                  <p className="mt-3 break-words leading-relaxed text-ink/75">{post.excerpt}</p>
                )}
              </article>
            </Reveal>
          ))}
        </div>
      )}
    </Section>
  )
}
