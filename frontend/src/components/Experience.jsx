import { formatDate } from '../lib/format'
import { LoadError, Reveal, Section, Skeleton } from './ui'

function ExperienceCard({ e, delay }) {
  const range = `${formatDate(e.start_date)} – ${e.is_current ? 'Present' : formatDate(e.end_date)}`
  return (
    <Reveal delay={delay}>
      <div className="rounded-2xl border border-ink/10 bg-white p-6 transition hover:-translate-y-1 hover:shadow-lg">
        <div className="flex flex-wrap items-center gap-3">
          <p className="text-sm font-semibold uppercase tracking-widest text-accent2">
            {e.is_current ? 'Current' : 'Past'}
          </p>
          {e.is_current && (
            <span className="rounded-full bg-accent/10 px-2.5 py-0.5 text-xs font-medium text-accent">
              Ongoing
            </span>
          )}
        </div>
        <h3 className="mt-2 break-words text-xl font-semibold">{e.position}</h3>
        <p className="mt-1 break-words text-ink/75">{e.company_name}</p>
        <p className="mt-3 text-sm text-ink/60">{range}</p>
        {e.description && (
          <p className="mt-4 break-words leading-relaxed text-ink/80">{e.description}</p>
        )}
      </div>
    </Reveal>
  )
}

export default function Experience({ number, experience }) {
  if (experience.status === 'success' && experience.data.length === 0) return null

  return (
    <Section id="experience" number={number} title="Experience" tone="white">
      {experience.status === 'loading' && (
        <div className="space-y-4">
          <Skeleton className="h-40" />
          <Skeleton className="h-40" />
        </div>
      )}
      {experience.status === 'error' && <LoadError what="experience" />}
      {experience.status === 'success' && (
        <div className="space-y-6">
          {experience.data.map((e, i) => (
            <ExperienceCard key={e.experience_id} e={e} delay={i * 90} />
          ))}
        </div>
      )}
    </Section>
  )
}
