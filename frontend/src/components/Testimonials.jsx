import { formatDate } from '../lib/format'
import { LoadError, Reveal, Section, Skeleton, StarIcon } from './ui'

function Stars({ rating }) {
  if (!rating) return null
  return (
    <div className="flex text-accent2" role="img" aria-label={`${rating} out of 5 stars`}>
      {[1, 2, 3, 4, 5].map((n) => (
        <StarIcon key={n} filled={n <= rating} />
      ))}
    </div>
  )
}

// Renders nothing once we know there are zero testimonials. While loading or on
// error, App still mounts this (see showTestimonials in App.jsx) so a
// skeleton/error can show instead of the section just popping in unannounced.
export default function Testimonials({ number, testimonials }) {
  if (testimonials.status === 'success' && testimonials.data.length === 0) return null

  return (
    <Section id="testimonials" number={number} title="Testimonials" tone="white">
      {testimonials.status === 'loading' && (
        <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
          {[0, 1, 2].map((i) => (
            <Skeleton key={i} className="h-48" />
          ))}
        </div>
      )}
      {testimonials.status === 'error' && <LoadError what="testimonials" />}
      {testimonials.status === 'success' && (
        <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
          {testimonials.data.map((t, i) => (
            <Reveal key={t.testimonial_id} delay={i * 90} className="h-full">
              <figure className="flex h-full flex-col rounded-3xl border border-ink/10 bg-white p-6 transition hover:-translate-y-1 hover:shadow-lg">
                <Stars rating={t.rating} />
                <blockquote className="mt-4 flex-1 break-words leading-relaxed text-ink/80">
                  “{t.content}”
                </blockquote>
                <figcaption className="mt-6">
                  <p className="break-words font-semibold">{t.client_name}</p>
                  {t.client_company && (
                    <p className="break-words text-sm text-ink/60">{t.client_company}</p>
                  )}
                  {t.date_received && (
                    <p className="mt-1 text-xs text-ink/50">{formatDate(t.date_received)}</p>
                  )}
                </figcaption>
              </figure>
            </Reveal>
          ))}
        </div>
      )}
    </Section>
  )
}
