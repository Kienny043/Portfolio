import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // Local dev: frontend on :5173, Django on :8000. Forwarding /api keeps every
    // request same-origin (relative), exactly like production — no CORS needed.
    proxy: {
      '/api': 'http://localhost:8000',
    },
  },
})
