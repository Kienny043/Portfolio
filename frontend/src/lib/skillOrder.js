// Display order for skills. The API returns them alphabetically; unknown
// skills (e.g. added later in the DB) go after these, alphabetically.
export const SKILL_ORDER = [
  'Python',
  'Django',
  'Django REST Framework',
  'PostgreSQL',
  'JWT Auth',
  'React',
  'Vite',
  'Tailwind CSS',
  'Recharts',
  'Leaflet',
  'Git & GitHub',
  'Render',
  'AI API Integration',
  'WeasyPrint / ReportLab',
]

export function sortSkills(skills) {
  const rank = (s) => {
    const i = SKILL_ORDER.indexOf(s.category)
    return i === -1 ? SKILL_ORDER.length : i
  }
  return [...skills].sort(
    (a, b) => rank(a) - rank(b) || (a.category || '').localeCompare(b.category || ''),
  )
}
