import { useState } from 'react'
import { apiPost } from '../lib/api'
import { Reveal, Section } from './ui'

const EMPTY = { sender_name: '', sender_email: '', subject: '', message: '' }

const inputClass =
  'w-full rounded-xl border border-ink/20 bg-white px-4 py-3 outline-none transition focus:border-accent focus:ring-2 focus:ring-accent/20'

function Field({ label, error, children }) {
  return (
    <label className="block">
      <span className="mb-1.5 block text-sm font-medium">{label}</span>
      {children}
      {error && <span className="mt-1 block text-sm text-accent2">{error}</span>}
    </label>
  )
}

export default function Contact({ number }) {
  const [form, setForm] = useState(EMPTY)
  // status: 'idle' | 'pending' | 'success' | 'error'
  const [status, setStatus] = useState('idle')
  const [fieldErrors, setFieldErrors] = useState({})
  const [errorMessage, setErrorMessage] = useState('')

  const update = (name) => (e) => setForm((f) => ({ ...f, [name]: e.target.value }))

  async function onSubmit(e) {
    e.preventDefault()
    setStatus('pending')
    setFieldErrors({})
    setErrorMessage('')

    try {
      const { status: code, data } = await apiPost('/contact/', form)
      if (code === 201) {
        setStatus('success')
        setForm(EMPTY)
      } else if (code === 400 && data) {
        // DRF returns { field: ["message", ...] }
        const errors = {}
        for (const [field, msgs] of Object.entries(data)) {
          errors[field] = Array.isArray(msgs) ? msgs.join(' ') : String(msgs)
        }
        setFieldErrors(errors)
        setErrorMessage('Please fix the highlighted fields and try again.')
        setStatus('error')
      } else if (code === 429) {
        setErrorMessage('You’ve sent a few messages already. Please try again later.')
        setStatus('error')
      } else {
        setErrorMessage('Something went wrong on my end. Please try again in a moment.')
        setStatus('error')
      }
    } catch {
      setErrorMessage('Couldn’t reach the server. Check your connection and try again.')
      setStatus('error')
    }
  }

  const pending = status === 'pending'

  return (
    <Section id="contact" number={number} title="Contact">
      <div className="grid gap-8 md:grid-cols-[1fr_1.4fr] md:gap-10">
        <Reveal>
        <p className="max-w-sm text-lg leading-relaxed text-ink/75">
          Have a project in mind, or just want to say hello? Send me a message and I’ll get back to
          you.
        </p>
        </Reveal>

        <Reveal delay={120}>
        <form onSubmit={onSubmit} noValidate className="space-y-5">
          <div className="grid gap-5 sm:grid-cols-2">
            <Field label="Name" error={fieldErrors.sender_name}>
              <input
                required
                maxLength={200}
                autoComplete="name"
                value={form.sender_name}
                onChange={update('sender_name')}
                className={inputClass}
              />
            </Field>
            <Field label="Email" error={fieldErrors.sender_email}>
              <input
                required
                type="email"
                maxLength={254}
                autoComplete="email"
                value={form.sender_email}
                onChange={update('sender_email')}
                className={inputClass}
              />
            </Field>
          </div>
          <Field label="Subject" error={fieldErrors.subject}>
            <input
              maxLength={200}
              value={form.subject}
              onChange={update('subject')}
              className={inputClass}
            />
          </Field>
          <Field label="Message" error={fieldErrors.message}>
            <textarea
              required
              rows={6}
              maxLength={5000}
              value={form.message}
              onChange={update('message')}
              className={inputClass}
            />
          </Field>

          <button
            type="submit"
            disabled={pending}
            className="rounded-full bg-accent px-7 py-3 font-medium text-paper transition hover:bg-accent2 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {pending ? 'Sending…' : 'Send message'}
          </button>

          <div aria-live="polite">
            {status === 'success' && (
              <p className="rounded-xl border border-accent/30 bg-accent/5 px-4 py-3 text-accent">
                Thanks — your message was sent. I’ll reply soon.
              </p>
            )}
            {status === 'error' && (
              <p className="rounded-xl border border-accent2/40 bg-accent2/5 px-4 py-3 text-accent2">
                {errorMessage}
              </p>
            )}
          </div>
        </form>
        </Reveal>
      </div>
    </Section>
  )
}
