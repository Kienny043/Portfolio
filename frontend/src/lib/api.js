import { useEffect, useState } from 'react'

// The API is same-origin: in production Django serves both the React app and /api/,
// and in local dev the Vite dev server proxies /api to Django (see vite.config.js).
const API_BASE = '/api'

const url = (path) => `${API_BASE}${path}`

export async function apiGet(path, signal) {
  const res = await fetch(url(path), { signal, headers: { Accept: 'application/json' } })
  if (!res.ok) throw new Error(`Request to ${path} failed (${res.status})`)
  return res.json()
}

/** POST JSON. Resolves with { status, data } for any HTTP response; rejects only on network failure. */
export async function apiPost(path, body) {
  const res = await fetch(url(path), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
    body: body === undefined ? undefined : JSON.stringify(body),
  })
  let data = null
  try {
    data = await res.json()
  } catch {
    // empty body (e.g. analytics 201)
  }
  return { status: res.status, data }
}

/** GET a path once on mount. state.status is 'loading' | 'success' | 'error'. */
export function useApi(path) {
  const [state, setState] = useState({ status: 'loading', data: null })

  useEffect(() => {
    const controller = new AbortController()
    apiGet(path, controller.signal)
      .then((data) => setState({ status: 'success', data }))
      .catch((err) => {
        if (err.name !== 'AbortError') setState({ status: 'error', data: null })
      })
    return () => controller.abort()
  }, [path])

  return state
}
