import { useEffect, useState } from 'react'

function MenuIcon({ open }) {
  return (
    <svg
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      aria-hidden="true"
    >
      {open ? <path d="M6 6l12 12M18 6 6 18" /> : <path d="M4 7h16M4 12h16M4 17h16" />}
    </svg>
  )
}

export default function Nav({ links }) {
  const [open, setOpen] = useState(false)
  const [activeId, setActiveId] = useState(null)
  const linkIds = links.map((l) => l.id).join('|')

  useEffect(() => {
    if (!open) return
    const onKey = (e) => e.key === 'Escape' && setOpen(false)
    // Close if the viewport grows past the mobile breakpoint.
    const mq = window.matchMedia('(min-width: 768px)')
    const onChange = (e) => e.matches && setOpen(false)
    window.addEventListener('keydown', onKey)
    mq.addEventListener('change', onChange)
    return () => {
      window.removeEventListener('keydown', onKey)
      mq.removeEventListener('change', onChange)
    }
  }, [open])

  // Highlight whichever section the scroll position is currently "in", so the
  // active link tracks scrolling (not just clicks). A fixed trigger line just
  // below the sticky nav is more reliable than an IntersectionObserver band for
  // this: a band can sit lower than a short section's whole height (e.g. Skills),
  // skipping straight to the next one. Active = the last section whose top has
  // already scrolled past the trigger line.
  useEffect(() => {
    const sections = linkIds
      .split('|')
      .filter(Boolean)
      .map((id) => document.getElementById(id))
      .filter(Boolean)
    if (sections.length === 0) return

    const TRIGGER_OFFSET = 120 // px below the viewport top (clears the sticky nav)
    let raf = null

    const update = () => {
      raf = null
      let current = null
      for (const el of sections) {
        if (el.getBoundingClientRect().top <= TRIGGER_OFFSET) current = el
      }
      // Right at the bottom of the page, always land on the last section (its
      // top may sit above the trigger line without ever crossing it exactly,
      // e.g. if it's taller than the viewport).
      const atBottom =
        window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 2
      if (atBottom) current = sections[sections.length - 1]
      setActiveId(current ? current.id : null)
    }
    const onScroll = () => {
      if (raf === null) raf = requestAnimationFrame(update)
    }

    update()
    window.addEventListener('scroll', onScroll, { passive: true })
    window.addEventListener('resize', onScroll)
    return () => {
      window.removeEventListener('scroll', onScroll)
      window.removeEventListener('resize', onScroll)
      if (raf !== null) cancelAnimationFrame(raf)
    }
  }, [linkIds])

  const linkClass = (id) =>
    `transition-colors hover:text-accent2 ${id === activeId ? 'text-accent2 font-semibold' : ''}`

  return (
    <header className="sticky top-0 z-30 border-b border-ink/10 bg-paper/90 backdrop-blur">
      <nav
        className="mx-auto flex max-w-6xl items-center justify-between px-5 py-3.5 sm:px-6 md:py-4"
        aria-label="Main"
      >
        <a href="#top" className="font-display text-lg font-semibold text-accent">
          Kien
        </a>

        {/* Desktop links */}
        <ul className="hidden items-center gap-7 text-sm font-medium md:flex">
          {links.map((l) => (
            <li key={l.id}>
              <a
                href={`#${l.id}`}
                aria-current={l.id === activeId ? 'true' : undefined}
                className={linkClass(l.id)}
              >
                {l.label}
              </a>
            </li>
          ))}
        </ul>

        {/* Mobile toggle */}
        <button
          type="button"
          onClick={() => setOpen((o) => !o)}
          aria-expanded={open}
          aria-controls="mobile-menu"
          aria-label={open ? 'Close menu' : 'Open menu'}
          className="-mr-2 rounded-full p-2 text-ink transition hover:bg-accent/10 md:hidden"
        >
          <MenuIcon open={open} />
        </button>
      </nav>

      {open && (
        <ul
          id="mobile-menu"
          className="border-t border-ink/10 bg-paper px-5 pb-4 pt-2 motion-safe:animate-fade-down md:hidden"
        >
          {links.map((l) => (
            <li key={l.id}>
              <a
                href={`#${l.id}`}
                onClick={() => setOpen(false)}
                aria-current={l.id === activeId ? 'true' : undefined}
                className={`block border-b border-ink/5 py-3.5 text-lg font-medium last:border-0 hover:text-accent2 ${l.id === activeId ? 'text-accent2 font-semibold' : ''}`}
              >
                {l.label}
              </a>
            </li>
          ))}
        </ul>
      )}
    </header>
  )
}
