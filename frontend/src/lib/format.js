const DATE_ONLY = /^(\d{4})-(\d{2})-(\d{2})$/

/**
 * Format an API date for display in the viewer's local time zone.
 * - Timestamps (with a UTC offset) are converted to local time by the Date parser.
 * - Date-only values ("2026-06-30") have no time zone; they're shown as-is,
 *   not shifted, by building the Date in local time.
 */
export function formatDate(value) {
  if (!value) return ''
  const m = DATE_ONLY.exec(value)
  const date = m ? new Date(+m[1], +m[2] - 1, +m[3]) : new Date(value)
  if (Number.isNaN(date.getTime())) return ''
  return date.toLocaleDateString(undefined, { year: 'numeric', month: 'long', day: 'numeric' })
}

export function isFuture(value) {
  const m = DATE_ONLY.exec(value || '')
  const date = m ? new Date(+m[1], +m[2] - 1, +m[3]) : new Date(value)
  return date.getTime() > Date.now()
}

export function yearOf(value) {
  const m = DATE_ONLY.exec(value || '')
  return m ? m[1] : String(new Date(value).getFullYear())
}
