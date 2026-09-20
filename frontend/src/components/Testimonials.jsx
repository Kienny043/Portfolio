import { formatDate } from '../lib/format'
import { Reveal, Section, StarIcon } from './ui'

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

// Renders nothing until there is at least one testimonial (App only mounts it then).
export default function Testimonials({ number, items }) {
  return (
    <Section id="testimonials" number={number} title="Testimonials" tone="white">
      <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
        {items.map((t, i) => (
          <Reveal key={t.testimonial_id} delay={i * 90} className="h-full">
          <figure
            className="flex h-full flex-col rounded-3xl border border-ink/10 bg-white p-6 transition hover:-translate-y-1 hover:shadow-lg"
          >
            <Stars rating={t.rating} />
            <blockquote className="mt-4 flex-1 leading-relaxed text-ink/80">“{t.content}”</blockquote>
            <figcaption className="mt-6">
              <p className="font-semibold">{t.client_name}</p>
              {t.client_company && <p className="text-sm text-ink/60">{t.client_company}</p>}
              {t.date_received && (
                <p className="mt-1 text-xs text-ink/50">{formatDate(t.date_received)}</p>
              )}
            </figcaption>
          </figure>
          </Reveal>
        ))}
      </div>
    </Section>
  )
}
