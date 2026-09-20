import { formatDate, isFuture, yearOf } from '../lib/format'
import { LoadError, Reveal, Section, Skeleton } from './ui'

function EducationCard({ e }) {
  const when = e.end_date
    ? isFuture(e.end_date)
      ? `Expected ${yearOf(e.end_date)}`
      : formatDate(e.end_date)
    : ''
  return (
    <div className="rounded-2xl border border-ink/10 bg-white p-6 transition hover:-translate-y-1 hover:shadow-lg">
      <p className="text-sm font-semibold uppercase tracking-widest text-accent2">Education</p>
      <h3 className="mt-2 text-xl font-semibold">{e.institution}</h3>
      {e.degree && <p className="mt-1 text-ink/75">{e.degree}</p>}
      {when && <p className="mt-3 text-sm text-ink/60">{when}</p>}
      {e.grade && <p className="text-sm text-ink/60">Grade: {e.grade}</p>}
    </div>
  )
}

export default function About({ number, profile, education }) {
  const p = profile.status === 'success' ? profile.data[0] : null
  const edu = education.status === 'success' ? education.data : []

  if (profile.status === 'success' && !p) return null

  return (
    <Section id="about" number={number} title="About">
      {profile.status === 'loading' && (
        <div className="space-y-3">
          <Skeleton className="h-5 w-full max-w-2xl" />
          <Skeleton className="h-5 w-2/3" />
        </div>
      )}
      {profile.status === 'error' && <LoadError what="the about section" />}
      {p && (
        <div className="grid gap-8 md:grid-cols-[1.5fr_1fr] md:gap-10">
          <Reveal>
            <p className="text-lg leading-relaxed text-ink/80">{p.bio}</p>
          </Reveal>
          {edu.length > 0 && (
            <Reveal delay={120} className="space-y-4">
              {edu.map((e) => (
                <EducationCard key={e.education_id} e={e} />
              ))}
            </Reveal>
          )}
        </div>
      )}
    </Section>
  )
}
