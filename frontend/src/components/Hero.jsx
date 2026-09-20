import { useState } from 'react'
import { ImagePlaceholder } from './ui'

const PHOTO_SRC = '/images/Profile_photo.jpg'

const INTRO =
  'Fourth-year BSIT student building full-stack systems that real institutions actually run on.'

/** Profile photo; falls back to the dashed "Add Photo" box if the file is missing or fails to load. */
function HeroPhoto() {
  const [failed, setFailed] = useState(false)
  if (failed) return <ImagePlaceholder kind="photo" className="aspect-[4/5] w-full" />
  return (
    <img
      src={PHOTO_SRC}
      alt="Portrait of Kienny"
      onError={() => setFailed(true)}
      className="aspect-[4/5] w-full rounded-2xl border border-ink/10 object-cover object-top shadow-sm"
    />
  )
}

export default function Hero() {
  return (
    <section id="top">
      <div className="mx-auto grid max-w-6xl items-center gap-10 px-5 py-12 sm:px-6 md:grid-cols-[1.3fr_1fr] md:gap-12 md:py-24">
        <div>
          <p className="mb-6 inline-block max-w-full rounded-full bg-accent/10 px-4 py-1.5 text-xs font-semibold text-accent motion-safe:animate-fade-up sm:text-sm">
            Full-Stack Developer · Probably Debugging Right Now
          </p>

          <h1 className="mb-6 text-4xl font-semibold leading-[1.08] tracking-tight text-ink motion-safe:animate-fade-up [animation-delay:100ms] sm:text-5xl md:text-6xl">
            I’m Kienny. I build software that survives contact with the real world.
          </h1>

          <p className="max-w-xl text-base leading-relaxed text-ink/75 motion-safe:animate-fade-up [animation-delay:200ms] sm:text-lg">
              {INTRO}
            </p>

          <div className="mt-8 flex flex-wrap gap-3 motion-safe:animate-fade-up [animation-delay:300ms] sm:gap-4">
            <a
              href="#projects"
              className="rounded-full bg-accent px-6 py-3 font-medium text-paper transition hover:-translate-y-0.5 hover:bg-accent2"
            >
              View my work
            </a>
            <a
              href="#contact"
              className="rounded-full border border-accent px-6 py-3 font-medium text-accent transition hover:-translate-y-0.5 hover:bg-accent hover:text-paper"
            >
              Get in touch
            </a>
          </div>
        </div>

        <div className="w-full max-w-[16rem] justify-self-center motion-safe:animate-fade-up [animation-delay:250ms] sm:max-w-xs md:max-w-sm md:justify-self-end">
          <HeroPhoto />
        </div>
      </div>
    </section>
  )
}
