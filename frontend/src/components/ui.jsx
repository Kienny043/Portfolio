import { useEffect, useRef, useState } from 'react'

/** Fades/slides children in once they scroll into view. Wrap cards; don't put it on hover-animated elements. */
export function Reveal({ children, delay = 0, className = '' }) {
  const ref = useRef(null)
  // Without IntersectionObserver support, just show everything.
  const [shown, setShown] = useState(() => !('IntersectionObserver' in window))

  useEffect(() => {
    const el = ref.current
    if (!el || shown) return
    const io = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setShown(true)
          io.disconnect()
        }
      },
      { threshold: 0.1, rootMargin: '0px 0px -40px 0px' },
    )
    io.observe(el)
    return () => io.disconnect()
  }, [shown])

  return (
    <div
      ref={ref}
      style={{ '--delay': `${delay}ms` }}
      className={`reveal ${shown ? 'is-visible' : ''} ${className}`}
    >
      {children}
    </div>
  )
}

// Small shared building blocks: section shell, placeholders, skeleton, icons.

export function Section({ id, number, title, children, tone = 'paper' }) {
  return (
    <section id={id} className={tone === 'white' ? 'bg-white/60' : ''}>
      <div className="mx-auto max-w-6xl px-5 py-16 sm:px-6 md:py-24">
        <Reveal className="mb-8 flex items-center gap-4 md:mb-10">
          <span className="flex h-9 w-9 items-center justify-center rounded-full bg-accent text-sm font-semibold text-paper">
            {String(number).padStart(2, '0')}
          </span>
          <h2 className="text-3xl font-semibold tracking-tight md:text-4xl">{title}</h2>
        </Reveal>
        {children}
      </div>
    </section>
  )
}

export function Pill({ children, tone = 'accent' }) {
  const styles =
    tone === 'accent2' ? 'bg-accent2/10 text-accent2' : 'bg-accent/10 text-accent'
  return (
    <span className={`inline-block rounded-full px-3 py-1 text-sm font-medium ${styles}`}>
      {children}
    </span>
  )
}

export function Skeleton({ className = '' }) {
  return <div className={`animate-pulse rounded-xl bg-ink/10 ${className}`} />
}

export function LoadError({ what }) {
  return (
    <p className="rounded-xl border border-accent2/40 bg-accent2/5 px-4 py-3 text-sm text-accent2">
      Couldn’t load {what}. Please try refreshing the page.
    </p>
  )
}

/** Dashed-border stand-in for a missing image. kind: 'photo' | 'screenshot' */
export function ImagePlaceholder({ kind = 'screenshot', className = '' }) {
  const isPhoto = kind === 'photo'
  return (
    <div
      role="img"
      aria-label={isPhoto ? 'Add Photo' : 'Add Screenshot'}
      className={`flex flex-col items-center justify-center gap-2 rounded-2xl border-2 border-dashed border-ink/25 text-ink/45 ${className}`}
    >
      {isPhoto ? <CameraIcon /> : <ImageIcon />}
      <span className="text-sm font-medium">{isPhoto ? 'Add Photo' : 'Add Screenshot'}</span>
    </div>
  )
}

const iconProps = {
  width: 36,
  height: 36,
  viewBox: '0 0 24 24',
  fill: 'none',
  stroke: 'currentColor',
  strokeWidth: 1.5,
  strokeLinecap: 'round',
  strokeLinejoin: 'round',
  'aria-hidden': true,
}

export function CameraIcon() {
  return (
    <svg {...iconProps}>
      <path d="M4 8a2 2 0 0 1 2-2h1.5l1.3-2h6.4l1.3 2H18a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V8Z" />
      <circle cx="12" cy="13" r="3.5" />
    </svg>
  )
}

export function ImageIcon() {
  return (
    <svg {...iconProps}>
      <rect x="3" y="4" width="18" height="16" rx="2" />
      <circle cx="9" cy="10" r="1.6" />
      <path d="m21 16-5-5-8 8" />
    </svg>
  )
}

export function StarIcon({ filled }) {
  return (
    <svg
      width="18"
      height="18"
      viewBox="0 0 24 24"
      fill={filled ? 'currentColor' : 'none'}
      stroke="currentColor"
      strokeWidth="1.5"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d="m12 3 2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1-4.4-4.3 6.1-.9L12 3Z" />
    </svg>
  )
}
