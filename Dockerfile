# Single-service image: builds the React frontend, then serves it together with the
# Django API from one gunicorn process (one origin, no CORS). Build context = repo root.
#
# NOTE: this image never runs `migrate`. The Aiven tables are managed = False and
# already exist; migrating could create unwanted Django-internal tables in that database.

# ---- Stage 1: build the frontend -------------------------------------------------
FROM node:22 AS frontend
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# ---- Stage 2: Django + the built frontend ---------------------------------------
FROM python:3.13-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=10000

# Layout matters: settings.py looks for the build at <backend>/../frontend/dist.
WORKDIR /app/backend
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ ./
COPY --from=frontend /app/frontend/dist /app/frontend/dist

# collectstatic loads Django settings, which require a secret key outside DEBUG.
# This throwaway value is scoped to this one command and is not baked into the image;
# the real DJANGO_SECRET_KEY is supplied at runtime.
RUN DJANGO_SECRET_KEY=build-time-only python manage.py collectstatic --noinput

RUN useradd --system --no-create-home app
USER app

EXPOSE 10000
CMD exec gunicorn config.wsgi:application --workers 2 --bind 0.0.0.0:$PORT
