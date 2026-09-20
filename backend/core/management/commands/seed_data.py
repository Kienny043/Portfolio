"""Seed the existing Aiven tables with the portfolio owner's real content.

    python manage.py seed_data             # insert
    python manage.py seed_data --dry-run   # do everything, then roll back
    python manage.py seed_data --media-only  # only add missing project_media rows

Refuses to run if the owner's user row already exists, so it never duplicates.
The password hash is read as-is from SEED_PASSWORD_HASH (already hashed; it is
never re-hashed, and is kept out of source control).
"""
import os
from datetime import date

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from core.models import (
    Education,
    Profile,
    Project,
    ProjectMedia,
    ProjectTag,
    Skills,
    Users,
)

EMAIL = "carabido.carlkien.dll@gmail.com"

BIO = (
    "Fourth-year BSIT student at Dalubhasaan ng Lungsod ng Lucena, based in "
    "Quezon Province, Philippines. Full-stack developer working with Django "
    "REST Framework and React."
)

SKILLS = [
    "Python", "Django", "Django REST Framework", "PostgreSQL", "JWT Auth",
    "React", "Vite", "Tailwind CSS", "Recharts", "Leaflet",
    "Git & GitHub", "Render", "AI API Integration", "WeasyPrint / ReportLab",
]

PROJECTS = [
    {
        "title": "PDRRMO Integrated Management System",
        "description": (
            "A full-stack disaster risk reduction and management platform for the "
            "Provincial DRRM Office of Quezon Province. Two modules — iREPORTS for "
            "incident reporting and AI-assisted situational report generation, and "
            "iPROVISION for inventory, training, and personnel — serving four user "
            "roles across 41 municipalities."
        ),
        "demo_url": None,
        "is_featured": True,
        "display_order": 1,
        "media": "/images/projects/PDRRMO-system.png",
        "tags": ["Django REST Framework", "React", "PostgreSQL", "Leaflet", "AI SitRep Generation"],
    },
    {
        "title": "quick-sitrep",
        "description": (
            "Replaces PDRRMO's manual copy-paste workflow: raw incident reports pasted "
            "in from Messenger get cleaned and structured by AI, then compiled into one "
            "combined province-wide situation report PDF. Live and running daily with "
            "the client's EOC team."
        ),
        "demo_url": "https://quick-sitrep.onrender.com",
        "is_featured": False,
        "display_order": 2,
        "media": "/images/projects/Quick-Sitrep.png",
        "tags": ["Django", "React", "Groq AI", "Render + Neon Postgres"],
    },
    {
        "title": "PDRRMO Inventory System",
        "description": (
            "Tracks equipment, staff records, training schedules, and a personnel "
            "training matrix spanning all 41 municipalities across 4 districts for "
            "PDRRMO's Inventory & Training Division."
        ),
        "demo_url": "https://pdrrmo-inventory.onrender.com",
        "is_featured": False,
        "display_order": 3,
        "media": "/images/projects/PDRRMO-inventory.png",
        "tags": ["Django", "Django REST Framework", "React", "PostgreSQL"],
    },
]


class Command(BaseCommand):
    help = "Insert the owner's user, profile, education, skills and projects."

    def add_arguments(self, parser):
        parser.add_argument(
            "--media-only", action="store_true",
            help="Only insert missing project_media rows for existing projects (by title).",
        )
        parser.add_argument(
            "--dry-run", action="store_true",
            help="Run all inserts inside a transaction, then roll back.",
        )

    def seed_media(self, dry_run):
        """Add one media row per seeded project that has none yet. Safe to rerun."""
        added = 0
        with transaction.atomic():
            for data in PROJECTS:
                project = Project.objects.filter(title=data["title"]).first()
                if project is None:
                    self.stdout.write(self.style.WARNING(f"Skipping (not found): {data['title']}"))
                    continue
                if ProjectMedia.objects.filter(project=project).exists():
                    continue
                ProjectMedia.objects.create(
                    project=project, media_url=data["media"], display_order=1
                )
                added += 1
            if dry_run:
                transaction.set_rollback(True)
        label = "Dry run (rolled back)" if dry_run else "Seeded"
        self.stdout.write(self.style.SUCCESS(f"{label}: project_media rows added={added}"))

    def handle(self, *args, dry_run=False, media_only=False, **options):
        if media_only:
            return self.seed_media(dry_run)
        password_hash = os.environ.get("SEED_PASSWORD_HASH", "").strip()
        if not password_hash.startswith("pbkdf2_"):
            raise CommandError(
                "SEED_PASSWORD_HASH must be set in .env to an already-hashed password."
            )
        if Users.objects.filter(email=EMAIL).exists():
            raise CommandError(f"User {EMAIL} already exists; refusing to seed twice.")

        with transaction.atomic():
            user = Users.objects.create(
                email=EMAIL,
                password=password_hash,  # inserted as-is, not re-hashed
                role="owner",
                created_at=timezone.now(),
            )
            profile = Profile.objects.create(
                user=user,
                firstname="Carl Kien",
                middlename="Villaflor",
                lastname="Carabido",
                bio=BIO,
                is_public=True,
            )
            Education.objects.create(
                profile=profile,
                institution="Dalubhasaan ng Lungsod ng Lucena",
                degree="Bachelor of Science in Information Technology",
                field_of_study="Information Technology",
                start_date=None,
                end_date=date(2026, 6, 30),  # expected graduation year: 2026
                grade=None,
            )
            for name in SKILLS:
                Skills.objects.create(
                    profile=profile, category=name, year_acquired=None, certification=None
                )
            for data in PROJECTS:
                fields = {k: v for k, v in data.items() if k not in ("tags", "media")}
                project = Project.objects.create(profile=profile, **fields)
                ProjectMedia.objects.create(
                    project=project, media_url=data["media"], display_order=1
                )
                for tag in data["tags"]:
                    ProjectTag.objects.create(project=project, tag_name=tag)

            summary = (
                f"user={Users.objects.count()} profile={Profile.objects.count()} "
                f"education={Education.objects.count()} skills={Skills.objects.count()} "
                f"projects={Project.objects.count()} tags={ProjectTag.objects.count()} "
                f"media={ProjectMedia.objects.count()}"
            )
            if dry_run:
                transaction.set_rollback(True)
                self.stdout.write(self.style.WARNING(f"Dry run (rolled back): {summary}"))
                return

        self.stdout.write(self.style.SUCCESS(f"Seeded: {summary}"))
