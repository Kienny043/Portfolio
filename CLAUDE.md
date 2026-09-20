# CLAUDE.md

Instructions for Claude Code when working in this repo. Read `portfolio-context.md` first for full design/content/schema details — this file is the quick-reference for conventions and commands.

## Project

Personal portfolio for Kienny (BSIT student). Two parts in one repo, deployed as **one Render Web Service** (same setup as quick-sitrep and the inventory system):
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
- `python manage.py collectstatic --noinput` — copy `frontend/dist` into `backend/staticfiles` (run after `npm run build`; Render does this in its build command)
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
- **Sections with zero rows render nothing, not an empty placeholder block** — this applies especially to Testimonials and Blog, which may start empty. Don't show a heading with no content under it.
- **Placeholders for missing images** (profile photo, project screenshots) are a dashed-border box with a stroke icon and a label ("Add Photo" / "Add Screenshot") — never a broken `<img>` or a stock/lorem image.

## Where things stand

- Design (colors, fonts, layout, copy) is finalized — see `portfolio-context.md` section 1–3.
- Schema is confirmed from Aiven — see section 4. Connection credentials are NOT in this repo; they're set directly as env vars in Render's dashboard.
- Still needed from Kienny before launch: real profile photo, project screenshots, at least one real testimonial.

## Deployment (Render)

**One Web Service** serves everything: the React app at `/` and the API at `/api/`. Nothing is committed with real values — set env vars in the service's Environment tab.

- `render.yaml` at the repo root is a Blueprint defining this service (commands, health check, env var names; secret values are `sync: false`, entered in the dashboard). The details below are the same settings, for reference or manual setup.
- Root Directory: **repo root** (leave blank — the build touches both `frontend/` and `backend/`)
- Runtime: Python. Versions are pinned by `.python-version` (3.13) and `.node-version` (22) at the repo root.
- Build command:
  ```
  cd frontend && npm install && npm run build && cd ../backend && pip install -r requirements.txt && python manage.py collectstatic --noinput
  ```
- Start command:
  ```
  cd backend && gunicorn config.wsgi:application --workers 2 --bind 0.0.0.0:$PORT
  ```
  - Keep `--workers 2` (sync workers): with `DB_CONN_MAX_AGE=0` that caps the API at ~2 concurrent Aiven connections. Aiven's small plans have very few slots; more workers/threads or a long `DB_CONN_MAX_AGE` caused "remaining connection slots are reserved" errors in dev.
- Health check path: `/api/health/` (doesn't touch the database)
- Env vars (the build needs `DJANGO_SECRET_KEY` too, because `collectstatic` loads Django settings — Render exposes env vars during the build):

| Variable | Value |
|---|---|
| `DATABASE_URL` | Aiven Service URI, ending `?sslmode=require` |
| `DJANGO_SECRET_KEY` | long random string (app refuses to start without it when `DJANGO_DEBUG` isn't `true`) |
| `DJANGO_DEBUG` | `false` (unset also means production mode) |
| `DJANGO_ALLOWED_HOSTS` | the service's host, no scheme, e.g. `portfolio.onrender.com` (Render's `RENDER_EXTERNAL_HOSTNAME` is also allowed automatically) |
| `DB_CONN_MAX_AGE` | `0` (also the default if unset) |
| `SEED_PASSWORD_HASH` | only needed to run `manage.py seed_data`; leave unset on Render (the DB is already seeded) |

- No `CORS_ALLOWED_ORIGINS` or `VITE_API_URL`: everything is same-origin. `django-cors-headers` is only installed when `DJANGO_DEBUG=true`, purely as a local convenience.
- How static serving works: `collectstatic` copies `frontend/dist` into `backend/staticfiles` (gzip-compressed by WhiteNoise); WhiteNoise serves it at the site root (`/assets/…` cached immutably, `/images/…`, `/favicon.svg`). Any non-`/api/` path that isn't a file returns `index.html` (`core.views.spa_index`); missing files with an extension and unknown `/api/…` paths are real 404s.
- Images live in `frontend/public/images/` and are referenced by root-relative paths (e.g. DB `project_media.media_url` = `/images/projects/…`), so they work unchanged.
