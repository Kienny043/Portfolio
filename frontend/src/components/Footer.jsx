export default function Footer({ name }) {
  return (
    <footer className="border-t border-ink/10">
      <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-2 px-5 py-8 text-center text-sm text-ink/60 sm:flex-row sm:px-6 sm:text-left">
        <p>
          © {new Date().getFullYear()} {name || 'Kien'}. All rights reserved.
        </p>
        <p>Built with way too much coffee in Quezon Province.</p>
      </div>
    </footer>
  )
}
