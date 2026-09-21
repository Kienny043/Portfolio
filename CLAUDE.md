# CLAUDE.md

Instructions for Claude Code when working in this repo. Read `portfolio-context.md` first for full design/content/schema details — this file is the quick-reference for conventions and commands.

## Project

Personal portfolio for Kienny (BSIT student). Two parts in one repo, deployed as **one Docker-based Render Web Service** (same approach as the inventory system):
- `frontend/` — React + Vite. Built to `frontend/dist`, which Django serves.
- `backend/` — Django REST Framework API under `/api/`, reads/writes an existing Aiven PostgreSQL database, and serves the built frontend (WhiteNoise + a catch-all route returning `index.html`). Same origin in production, so no CORS.

The frontend is otherwise fully static content; the only reason a backend exists is to satisfy a class activity requiring a live DB connection (Aiven Postgres), and to handle the contact form + visitor analytics.

## Commands

**Frontend** (`frontend/`):
- `npm install` — install deps
- `npm run dev` — local dev server on :5173; proxies `/api` to Django on :8000 (see `vite.config.js`), so the app always uses relative `/api/...` paths
- `npm run build` — production build
- `npm run lint` — lint (set up ESLint if not already present)

**Backend** (`backend/`):
- `pip install -r requirements.txt`
- `python manage.py inspectdb > core/models_generated.py` — regenerate models from the live Aiven schema if it changes
- `python manage.py runserver` — local dev server on :8000 (run alongside `npm run dev`)
- `python manage.py collectstatic --noinput` — copy `frontend/dist` into `backend/staticfiles` (run after `npm run build`; the Dockerfile does this at image build time)
- Local production-style check: `npm run build` → `collectstatic` → `DJANGO_DEBUG=false DJANGO_SECRET_KEY=x python manage.py runserver 8001` serves the whole site from Django alone
- No `migrate` needed for the existing Aiven tables (`managed = False`) — only run migrations for anything Django-native (e.g. its own admin/session tables, if used)

## Conventions

- **Frontend:** Tailwind CSS utility classes, one component per section (`Hero`, `About`, `Skills`, `Projects`, `Testimonials`, `Blog`, `Contact`, `Footer`). Design tokens (colors, fonts) live in `tailwind.config.js` — reference them by name (`accent`, `accent2`, `ink`, `paper`), never hardcode hex in components.
- **Backend:** DRF `ReadOnlyModelViewSet` for anything that's just displayed (profile, education, experience, skills, projects, testimonials, blog). Plain `APIView`/`CreateAPIView` for `contact_inquiry` (POST-only) and `analytics` (POST-only, plus a small read endpoint for a visitor count if implemented).
- **Frontend API calls are relative** (`/api/...`, see `src/lib/api.js`) — never an absolute URL and no `VITE_*` env vars. Vite proxies in dev; Django is same-origin in production.
- **Env vars, never hardcoded secrets** (full reference in "Deployment" below). Never commit a `.env` file — it's git-ignored; only `backend/.env.example` (placeholders) is committed.

## Hard rules

- **Never serialize or return `users.password`** in any API response. Any serializer touching the `users` table must explicitly exclude it — don't rely on leaving it off a field list, exclude it defensively even if the viewset seems read-only elsewhere.
- **Don't let Django manage/migrate the existing Aiven tables.** They already exist with real (or professor-seeded) data. Models mapping to them need `managed = False` and the correct `db_table`.
- **Never run `python manage.py migrate` against the Aiven database — not in the Dockerfile, the start command, or a deploy hook.** The tables are `managed = False` and already exist; migrating would create Django-internal tables (`django_migrations`, etc.) in that database. The container's `CMD` runs gunicorn only.
- **Sections with zero rows render nothing, not an empty placeholder block** — this applies especially to Testimonials and Blog, which may start empty. Don't show a heading with no content under it.
- **Placeholders for missing images** (profile photo, project screenshots) are a dashed-border box with a stroke icon and a label ("Add Photo" / "Add Screenshot") — never a broken `<img>` or a stock/lorem image.

## Where things stand

- Design (colors, fonts, layout, copy) is finalized — see `portfolio-context.md` section 1–3.
- Schema is confirmed from Aiven — see section 4. Connection credentials are NOT in this repo; they're set directly as env vars in Render's dashboard.
- Still needed from Kienny before launch: real profile photo, project screenshots, at least one real testimonial.

## Deployment (Render, Docker)

**One Web Service**, built from the `Dockerfile` at the repo root and defined by `render.yaml` (a Blueprint). It serves the React app at `/` and the API at `/api/` from a single origin, so there is no CORS and no `VITE_API_URL`. Nothing is committed with real values — env vars are set in Render.

### The image (`Dockerfile`)
- **Stage 1** (`node:22`): `npm ci && npm run build` → `frontend/dist`.
- **Stage 2** (`python:3.13-slim`): installs `backend/requirements.txt`, copies `backend/`, copies the built `frontend/dist` to `/app/frontend/dist` (where `settings.FRONTEND_DIST` looks), and runs `collectstatic --noinput` with a throwaway build-time secret key.
- **`CMD exec gunicorn config.wsgi:application --workers 2 --bind 0.0.0.0:$PORT`** — nothing else. **No `migrate`** (see Hard rules). `PORT` defaults to 10000 and is overridden by Render.
- `--workers 2` (sync): with `DB_CONN_MAX_AGE=0` that caps the API at ~2 concurrent Aiven connections. Aiven's small plans have very few slots; more workers/threads or a long `DB_CONN_MAX_AGE` caused "remaining connection slots are reserved" errors in dev.
- `.dockerignore` keeps every `.env` (and `node_modules`, `.venv`, `dist`, `staticfiles`) out of the build context, so secrets can never end up in an image layer.

### Render service (`render.yaml`)
- Runtime `docker`, `dockerfilePath: ./Dockerfile`, context = repo root. No build/start commands: the Dockerfile owns both.
- Health check path: `/api/health/` (doesn't touch the database)
- Env vars:

| Variable | Value |
|---|---|
| `DATABASE_URL` | Aiven Service URI, ending `?sslmode=require` (`sync: false` — entered in the dashboard) |
| `DJANGO_SECRET_KEY` | generated by Render (`generateValue: true`) |
| `DJANGO_DEBUG` | `false` (set in `render.yaml`) |
| `DJANGO_ALLOWED_HOSTS` | the service's host, no scheme, e.g. `portfolio.onrender.com` (`sync: false`; Render's `RENDER_EXTERNAL_HOSTNAME` is also allowed automatically) |
| `DB_CONN_MAX_AGE` | `0` (set in `render.yaml`) |

- `SEED_PASSWORD_HASH` is only for running `manage.py seed_data` locally; it is not set on Render.

### How static serving works
`collectstatic` copies `frontend/dist` into `backend/staticfiles` (gzip-compressed by WhiteNoise), and WhiteNoise serves it at the site root (`/assets/…` cached immutably, `/images/…`, `/favicon.svg`). Any non-`/api/` path that isn't a file returns `index.html` (`core.views.spa_index`); missing files with an extension and unknown `/api/…` paths are real 404s. Images live in `frontend/public/images/` and are referenced by root-relative paths (e.g. `project_media.media_url` = `/images/projects/…`).

### Local commands
- Dev: `npm run dev` (:5173, proxies `/api` to Django) + `python manage.py runserver` (:8000). CORS is only installed when `DJANGO_DEBUG=true`.
- Image: `docker build -t portfolio .` then `docker run --rm -p 8000:10000 -e DATABASE_URL=... -e DJANGO_SECRET_KEY=... -e DJANGO_DEBUG=false -e DJANGO_ALLOWED_HOSTS=localhost portfolio` and open http://localhost:8000.
