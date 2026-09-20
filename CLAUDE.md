# CLAUDE.md

Instructions for Claude Code when working in this repo. Read `portfolio-context.md` first for full design/content/schema details — this file is the quick-reference for conventions and commands.

## Project

Personal portfolio for Kienny (BSIT student). Two parts in one repo, deployed as **two separate Render services**:
- `frontend/` — React + Vite, built to static files and deployed as a Render **Static Site**
- `backend/` — Django REST Framework API under `/api/`, reads/writes an existing Aiven PostgreSQL database, deployed as a Render **Web Service**

They live on different origins, so the frontend calls the API by absolute URL (`VITE_API_URL`) and the API allows the frontend's origin via CORS.

The frontend is otherwise fully static content; the only reason a backend exists is to satisfy a class activity requiring a live DB connection (Aiven Postgres), and to handle the contact form + visitor analytics.

## Commands

**Frontend** (`frontend/`):
- `npm install` — install deps
- `npm run dev` — local dev server on :5173; needs `frontend/.env` (copy `.env.example`) so `VITE_API_URL` points at Django on :8000
- `npm run build` — production build
- `npm run lint` — lint (set up ESLint if not already present)

**Backend** (`backend/`):
- `pip install -r requirements.txt`
- `python manage.py inspectdb > core/models_generated.py` — regenerate models from the live Aiven schema if it changes
- `python manage.py runserver` — local dev server on :8000 (run alongside `npm run dev`; CORS allows `http://localhost:5173` in DEBUG)
- No `migrate` needed for the existing Aiven tables (`managed = False`) — only run migrations for anything Django-native (e.g. its own admin/session tables, if used)

## Conventions

- **Frontend:** Tailwind CSS utility classes, one component per section (`Hero`, `About`, `Skills`, `Projects`, `Testimonials`, `Blog`, `Contact`, `Footer`). Design tokens (colors, fonts) live in `tailwind.config.js` — reference them by name (`accent`, `accent2`, `ink`, `paper`), never hardcode hex in components.
- **Backend:** DRF `ReadOnlyModelViewSet` for anything that's just displayed (profile, education, experience, skills, projects, testimonials, blog). Plain `APIView`/`CreateAPIView` for `contact_inquiry` (POST-only) and `analytics` (POST-only, plus a small read endpoint for a visitor count if implemented).
- **Frontend API calls use an absolute base URL** from `VITE_API_URL` (see `src/lib/api.js`), e.g. `https://<backend>.onrender.com/api` — include `/api`, no trailing slash. Vite bakes it in at build time.
- **Env vars, never hardcoded secrets** (full reference in "Deployment" below). Never commit a `.env` file — it's git-ignored; only the `.env.example` files (placeholders) are committed.

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

**Two services** from this one repo, each with its own Root Directory. (One combined service isn't possible on Render's native runtimes: the build needs both npm and pip.) Nothing is committed with real values — set env vars in each service's Environment tab.

### 1. Backend — Web Service
- Root Directory: `backend`
- Runtime: Python. Version pinned by `backend/.python-version` (3.13); if Render ignores it, set env var `PYTHON_VERSION` = `3.13.7`.
- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn config.wsgi:application --workers 2 --bind 0.0.0.0:$PORT`
  - Keep `--workers 2` (sync workers): with `DB_CONN_MAX_AGE=0` that caps the API at ~2 concurrent Aiven connections. Aiven's small plans have very few slots; more workers/threads or a long `DB_CONN_MAX_AGE` caused "remaining connection slots are reserved" errors in dev.
- Health check path: `/api/health/` (doesn't touch the database)
- Env vars:

| Variable | Value |
|---|---|
| `DATABASE_URL` | Aiven Service URI, ending `?sslmode=require` |
| `DJANGO_SECRET_KEY` | long random string (app refuses to start without it when `DJANGO_DEBUG` isn't `true`) |
| `DJANGO_DEBUG` | `false` (unset also means production mode) |
| `DJANGO_ALLOWED_HOSTS` | the backend's host, no scheme, e.g. `portfolio-api.onrender.com` (Render's `RENDER_EXTERNAL_HOSTNAME` is also allowed automatically) |
| `CORS_ALLOWED_ORIGINS` | the frontend's origin with scheme, no trailing slash, e.g. `https://portfolio-web.onrender.com` (comma-separate multiple). Unset in production = no cross-origin access, so the site can't load data. |
| `DB_CONN_MAX_AGE` | `0` (also the default if unset) |
| `SEED_PASSWORD_HASH` | only needed to run `manage.py seed_data`; leave unset on Render (the DB is already seeded) |

### 2. Frontend — Static Site
- Root Directory: `frontend`
- Build command: `npm install && npm run build`
- Publish directory: `dist`
- Node: pinned by `frontend/.node-version` (22, needed by Vite 8); if Render ignores it, set env var `NODE_VERSION` = `22`.
- Env vars:

| Variable | Value |
|---|---|
| `VITE_API_URL` | backend URL **including `/api`**, no trailing slash, e.g. `https://portfolio-api.onrender.com/api` |

- Vite bakes `VITE_*` values into the bundle **at build time**, not runtime. Set it before the first build, and after changing it trigger a new build (Manual Deploy → Clear build cache & deploy).
- Images live in `frontend/public/images/` and are served by the static site; `project_media.media_url` values are root-relative (`/images/projects/…`) and resolve against the frontend's origin.

### Deploy order
Each service needs the other's URL, so: create the **backend** first (set `CORS_ALLOWED_ORIGINS` to a placeholder for now) → create the **static site** with `VITE_API_URL` = the backend URL + `/api` → then set the backend's `DJANGO_ALLOWED_HOSTS` (if not relying on the automatic one) and `CORS_ALLOWED_ORIGINS` to the static site's URL and let it redeploy.
