import { useEffect, useRef } from 'react'
import { createPortal } from 'react-dom'

/**
 * Full-size image overlay. Closes on Esc, backdrop click, or the close button.
 * Rendered in a portal so ancestor transforms (card hover lift) can't break `fixed` positioning.
 */
export default function Lightbox({ src, alt, onClose }) {
  const closeRef = useRef(null)

  useEffect(() => {
    const opener = document.activeElement
    const onKey = (e) => e.key === 'Escape' && onClose()
    const scrollbar = window.innerWidth - document.documentElement.clientWidth
    const prevOverflow = document.body.style.overflow
    const prevPadding = document.body.style.paddingRight

    document.addEventListener('keydown', onKey)
    document.body.style.overflow = 'hidden' // lock background scroll
    document.body.style.paddingRight = `${scrollbar}px` // avoid layout jump
    closeRef.current?.focus()

    return () => {
      document.removeEventListener('keydown', onKey)
      document.body.style.overflow = prevOverflow
      document.body.style.paddingRight = prevPadding
      opener?.focus?.() // return focus to the thumbnail
    }
  }, [onClose])

  return createPortal(
    <div
      role="dialog"
      aria-modal="true"
      aria-label={alt}
      onClick={onClose}
      className="fixed inset-0 z-50 flex items-center justify-center bg-ink/80 p-4 backdrop-blur-sm motion-safe:animate-fade-down sm:p-8"
    >
      <button
        ref={closeRef}
        type="button"
        onClick={onClose}
        aria-label="Close image"
        className="absolute right-4 top-4 rounded-full bg-paper/15 p-2.5 text-paper transition hover:bg-paper/30 focus-visible:outline focus-visible:outline-2 focus-visible:outline-paper"
      >
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" aria-hidden="true">
          <path d="M6 6l12 12M18 6 6 18" />
        </svg>
      </button>
      {/* stopPropagation: clicking the image itself shouldn't close it */}
      <img
        src={src}
        alt={alt}
        onClick={(e) => e.stopPropagation()}
        className="max-h-full max-w-full rounded-xl bg-white object-contain shadow-2xl"
      />
    </div>,
    document.body,
  )
}
