import { sortSkills } from '../lib/skillOrder'
import { LoadError, Reveal, Section, Skeleton } from './ui'

// The `skills` table has no separate name column: `category` holds the skill's
// label (e.g. "Django"), so each row renders as one chip.
function SkillChip({ skill }) {
  const meta = [skill.year_acquired && `since ${skill.year_acquired}`, skill.certification]
    .filter(Boolean)
    .join(' · ')
  return (
    <li className="rounded-full border border-ink/10 bg-white px-4 py-2 text-sm font-medium transition hover:-translate-y-0.5 hover:border-accent/40 hover:shadow-md">
      {skill.category}
      {meta && <span className="ml-2 text-xs font-normal text-ink/55">{meta}</span>}
    </li>
  )
}

export default function Skills({ number, skills }) {
  if (skills.status === 'success' && skills.data.length === 0) return null

  return (
    <Section id="skills" number={number} title="Skills" tone="white">
      {skills.status === 'loading' && (
        <div className="flex flex-wrap gap-3">
          {Array.from({ length: 8 }, (_, i) => (
            <Skeleton key={i} className="h-10 w-28 rounded-full" />
          ))}
        </div>
      )}
      {skills.status === 'error' && <LoadError what="skills" />}
      {skills.status === 'success' && (
        <Reveal>
          <ul className="flex flex-wrap gap-2.5 sm:gap-3">
            {sortSkills(skills.data).map((s) => (
              <SkillChip key={s.skill_id} skill={s} />
            ))}
          </ul>
        </Reveal>
      )}
    </Section>
  )
}
