import { useCallback, useState } from 'react'
import Lightbox from './Lightbox'
import { ImagePlaceholder, LoadError, Pill, Reveal, Section, Skeleton } from './ui'

/** First screenshot if present; falls back to the placeholder if there's none or it fails to load.
 *  Only a real image is clickable (opens the lightbox) — the placeholder is inert. */
function Screenshot({ media, title }) {
  const [failed, setFailed] = useState(false)
  const [open, setOpen] = useState(false)
  const close = useCallback(() => setOpen(false), [])
  const first = [...media].sort((a, b) => (a.display_order ?? 0) - (b.display_order ?? 0))[0]

  if (!first || failed) return <ImagePlaceholder kind="screenshot" className="aspect-[2/1] w-full" />

  const alt = `${title} screenshot`
  return (
    <>
      <button
        type="button"
        onClick={() => setOpen(true)}
        aria-label={`View ${title} screenshot full size`}
        className="group relative block w-full cursor-zoom-in overflow-hidden rounded-2xl focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
      >
        <img
          src={first.media_url}
          alt={alt}
          loading="lazy"
          onError={() => setFailed(true)}
          className="aspect-[2/1] w-full rounded-2xl border border-ink/10 object-cover transition duration-300 group-hover:brightness-95"
        />
      </button>
      {open && <Lightbox src={first.media_url} alt={alt} onClose={close} />}
    </>
  )
}

function ProjectCard({ project }) {
  return (
    <article className="flex h-full flex-col rounded-3xl border border-ink/10 bg-white p-5 transition hover:-translate-y-1 hover:shadow-lg">
      <Screenshot media={project.media} title={project.title} />
      <div className="mt-5 flex flex-1 flex-col">
        {project.is_featured && (
          <p className="mb-2 text-xs font-semibold uppercase tracking-widest text-accent2">
            Featured
          </p>
        )}
        <h3 className="break-words text-2xl font-semibold leading-snug">{project.title}</h3>
        <p className="mt-3 flex-1 break-words leading-relaxed text-ink/75">{project.description}</p>

        {project.tags.length > 0 && (
          <ul className="mt-5 flex flex-wrap gap-2">
            {project.tags.map((t) => (
              <li key={t.tag_id}>
                <Pill>{t.tag_name}</Pill>
              </li>
            ))}
          </ul>
        )}

        <div className="mt-6">
          {project.demo_url ? (
            <a
              href={project.demo_url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 font-medium text-accent hover:text-accent2"
            >
              Visit live site <span aria-hidden="true">↗</span>
            </a>
          ) : (
            <span className="text-sm font-medium text-ink/55">In development</span>
          )}
        </div>
      </div>
    </article>
  )
}

export default function Projects({ number, projects }) {
  if (projects.status === 'success' && projects.data.length === 0) return null

  return (
    <Section id="projects" number={number} title="Projects">
      {projects.status === 'loading' && (
        <div className="grid gap-8 lg:grid-cols-3">
          {[0, 1, 2].map((i) => (
            <Skeleton key={i} className="h-96" />
          ))}
        </div>
      )}
      {projects.status === 'error' && <LoadError what="projects" />}
      {projects.status === 'success' && (
        <div className="grid gap-8 lg:grid-cols-3">
          {projects.data.map((p, i) => (
            <Reveal key={p.project_id} delay={i * 90} className="h-full">
              <ProjectCard project={p} />
            </Reveal>
          ))}
        </div>
      )}
    </Section>
  )
}
