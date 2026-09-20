# Portfolio Build Brief

Full-stack personal portfolio: **React + Vite** frontend, **Django REST Framework** backend, connected to a school-assigned **Aiven PostgreSQL** database. Frontend is otherwise static; the DRF API is the only dynamic layer, purely to satisfy the DB-connection class activity.

---

## 1. Design System

- **Fonts:** `Fraunces` (headings, serif) + `Work Sans` (body), via Google Fonts
- **Colors:**
  - `accent` (primary): `#6E1F2B` (maroon)
  - `accent2` (secondary/energy): `#B23A5C` (dark pink)
  - `ink` (text): `#141313` (near-black)
  - `paper` (background): `#F7F5EF` (off-white)
- **Style:** clean, minimal, generous whitespace, rounded pill tags, subtle card hover lift. Numbered section badges (01, 02, 03...) as small filled circles in `accent`.
- **Placeholders:** any missing image (profile photo, project screenshots) renders as a dashed-border box with a simple stroke icon (camera for photo, image icon for screenshots) and a label like "Add Photo" / "Add Screenshot" — never a broken image or lorem-ipsum image.
- **Tone:** confident, direct, first-person. Not corporate-stiff, not jokey — one or two light personal touches are fine (e.g. footer line), but keep the actual work descriptions serious.

## 2. Frontend Sections

1. **Nav** — sticky top bar, links to About / Skills / Projects / Testimonials / Contact
2. **Hero** — name, role tagline, 2-3 sentence intro, two CTA buttons ("View my work", "Get in touch"), photo placeholder
3. **About** — pulled from `profile.bio`
4. **Skills** — grouped by `skills.category`, showing `year_acquired` / `certification` where present
5. **Projects** — cards from `project`, each with:
   - nested `project_media` (screenshot placeholder if no rows)
   - `project_tag` chips
   - `demo_url` link if present, else "In development"
6. **Testimonials** *(new)* — cards from `testimonial`: `client_name`, `client_company`, `content`, `rating`, `date_received`. Skip rendering the section entirely if there are zero rows.
7. **Blog** *(new)* — preview cards from `blog_post` where `is_published = true`: `title`, `excerpt`, `published_at`. Skip rendering the section entirely if there are zero rows (don't show an empty section).
8. **Contact** — real form (name, email, subject, message) that POSTs to the backend and inserts into `contact_inquiry`. Show a success/error state after submit.
9. **Footer**

## 3. Known Real Content (seed data / reference — use if DB rows are empty, otherwise DB wins)

- **Name:** Kienny — 4th-year BSIT student, Dalubhasaan ng Lungsod ng Lucena (expected 2026), based in Quezon Province, PH
- **Skills:**
  - Backend: Python, Django, Django REST Framework, PostgreSQL, JWT Auth
  - Frontend: React, Vite, Tailwind CSS, Recharts, Leaflet
  - Tools: Git & GitHub, Render, AI API Integration, WeasyPrint / ReportLab
- **Projects:**
  - **PDRRMO Integrated Management System** — capstone, in development. Disaster risk reduction platform for the Provincial DRRM Office of Quezon Province. Modules: iREPORTS (incident reporting, AI-assisted SitRep generation) and iPROVISION (inventory, training, personnel). GIS mapping, hazard monitoring, compliance analytics.
  - **quick-sitrep** — live at `https://quick-sitrep.onrender.com`. Turns Messenger-pasted incident reports into AI-structured data and a combined PDF SitRep. Used daily by PDRRMO's EOC team.
  - **PDRRMO Inventory System** — live at `https://pdrrmo-inventory.onrender.com`. Equipment, staff, and training-schedule tracking for PDRRMO's Inventory & Training Division across 41 municipalities.

## 4. Backend (Django REST Framework)

- Connects to the existing Aiven PostgreSQL service — **tables already exist**, do not let Django create/migrate them. Run `manage.py inspectdb` against the live DB to generate matching models, then set `managed = False` on each and confirm `db_table` names match.
- **Schema (from Aiven, `public` schema):**
  - `profile`: profile_id, user_id, lastname, firstname, middlename, bio, is_public
  - `users`: user_id, email, password, role, created_at
  - `education`: education_id, profile_id, institution, degree, field_of_study, start_date, end_date, grade
  - `work_experience`: experience_id, profile_id, company_name, position, start_date, end_date, is_current, description
  - `skills`: skill_id, profile_id, category, year_acquired, certification
  - `project`: project_id, profile_id, title, description, demo_url, is_featured, display_order
  - `project_media`: project_media_id, project_id, media_url, display_order
  - `project_tag`: tag_id, project_id, tag_name
  - `testimonial`: testimonial_id, profile_id, client_name, client_company, content, rating, date_received
  - `blog_post`: post_id, profile_id, title, slug, excerpt, content, featured_image_url, published_at, is_published
  - `contact_inquiry`: inquiry_id, profile_id, sender_name, sender_email, subject, message, sent_at, is_read
  - `analytics`: analytics_id, profile_id, viewer_count, visited_time

- **Security — critical:** `users.password` must never be serialized or returned by any endpoint. Any serializer touching `users` must explicitly exclude it (don't rely on omission). The `users` table likely doesn't need a public endpoint at all.
- **Endpoints:**
  - `GET /api/profile/`
  - `GET /api/education/`
  - `GET /api/experience/` (work_experience)
  - `GET /api/skills/`
  - `GET /api/projects/` — nested media + tags
  - `GET /api/testimonials/`
  - `GET /api/blog/` — published posts only
  - `POST /api/contact/` — creates a `contact_inquiry` row from form input
  - `POST /api/analytics/` — logs a visit (increment viewer_count / insert visited_time)
  - `GET /api/analytics/count/` — optional, for a visible visitor counter
- **Config:**
  - DB connection via `DATABASE_URL` env var (Aiven connection string, `sslmode=require`) — never hardcode credentials
  - `django-cors-headers` enabled; allowed origins come from `CORS_ALLOWED_ORIGINS` (the deployed frontend's origin)
  - All read endpoints are read-only (`ReadOnlyModelViewSet` or plain `APIView` + GET)

## 5. Frontend ↔ Backend Integration

- Frontend fetches from `VITE_API_URL` (env var, absolute URL incl. `/api`) instead of hardcoded content for About/Skills/Projects/Testimonials/Blog
- Each section handles a loading state and an empty state (zero rows) gracefully — no broken layout
- Contact form: POST to `/api/contact/`, show inline success/error message, disable submit while pending
- Optional: fire the analytics POST once per page load

## 6. Deployment

- **Frontend:** Render Static Site (Root Directory `frontend`, build `npm install && npm run build`, publish `dist`), with `VITE_API_URL` set to the backend's URL
- **Backend:** Render Web Service (Root Directory `backend`, same platform as the other PDRRMO projects), with `DATABASE_URL` etc. set as env vars in Render's dashboard, not in code
- Exact commands and env var lists are in `CLAUDE.md` → Deployment.

## 7. Still Needed From Kienny

- Real profile photo
- Project screenshots (PDRRMO-IMS, quick-sitrep, Inventory System)
- At least one real testimonial, if obtainable (e.g. a PDRRMO contact)
- Aiven connection string / credentials (from the Aiven console, set directly as the Render env var — never pasted into chat or committed to the repo)
