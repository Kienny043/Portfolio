"""Seed the existing Aiven tables with the portfolio owner's real content.

    python manage.py seed_data              # insert
    python manage.py seed_data --dry-run    # do everything, then roll back
    python manage.py seed_data --media-only   # only add missing project_media rows
    python manage.py seed_data --extras-only  # only add missing work_experience / blog_post rows

Refuses to run if the owner's user row already exists, so it never duplicates.
The password hash is read as-is from SEED_PASSWORD_HASH (already hashed; it is
never re-hashed, and is kept out of source control).
"""
import os
from datetime import date, datetime, timezone as dt_timezone

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from core.models import (
    BlogPost,
    Education,
    Profile,
    Project,
    ProjectMedia,
    ProjectTag,
    Skills,
    Users,
    WorkExperience,
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

EXPERIENCE = [
    {
        "company_name": "Provincial Disaster Risk Reduction and Management Office (PDRRMO), Quezon Province",
        "position": "Full-Stack Developer (Capstone Project)",
        "start_date": date(2025, 1, 1),
        "end_date": None,
        "is_current": True,
        "description": (
            "Building the PDRRMO Integrated Management System, a disaster risk reduction "
            "platform with incident reporting, AI-assisted situational report generation, "
            "GIS mapping, and inventory/training management. Also independently built and "
            "deployed two standalone tools from this work — quick-sitrep and the PDRRMO "
            "Inventory System — both live and used by the office."
        ),
    },
]

BLOG_POSTS = [
    {
        "title": "Building Software a Government Office Actually Uses",
        "slug": "building-software-a-government-office-actually-uses",
        "excerpt": (
            "What changes when your capstone project isn't just for a grade — it's "
            "running live, every day, for people who need it to work."
        ),
        "content": (
            "Most capstone projects get graded and shelved. Mine didn't get that luxury.\n"
            "\n"
            "When I started building the PDRRMO Integrated Management System around "
            "January 2025, it was a school requirement first — a disaster risk reduction "
            "platform for the Provincial DRRM Office of Quezon Province, with two modules: "
            "iREPORTS for incident reporting and iPROVISION for inventory and training. But "
            "partway through, two smaller tools I built alongside it — quick-sitrep and the "
            "PDRRMO Inventory System — went from \"demo for my professor\" to \"thing the "
            "office actually opens every day.\"\n"
            "\n"
            "That changes how you build. quick-sitrep exists because PDRRMO's operations "
            "staff were manually copy-pasting incident reports out of Messenger every "
            "shift, cleaning them up by hand, and compiling them into a situation report "
            "one municipality at a time. I built it to take that raw, messy input, run it "
            "through AI to structure it, and spit out one combined province-wide SitRep as "
            "a PDF. The first version worked in my dev environment. It did not survive "
            "contact with real staff typing real reports at odd hours with typos and "
            "shorthand I hadn't anticipated. I rewrote the parsing logic three times before "
            "it held up.\n"
            "\n"
            "That's the actual lesson, more than any specific framework or library: a live "
            "client doesn't care that your code passed your own test cases. They care "
            "whether it works when they're tired, in a hurry, and the fire hasn't waited "
            "for anyone to write clean input.\n"
            "\n"
            "The Inventory System came out of a similar need — PDRRMO's Inventory & "
            "Training Division needed to track equipment and personnel training across 41 "
            "municipalities without another spreadsheet nobody keeps updated. It's deployed "
            "and ready; the office hasn't folded it into daily use yet, which is its own "
            "lesson — sometimes the code being done isn't the same as the rollout being "
            "done.\n"
            "\n"
            "I'm still building out the full Integrated Management System — GIS incident "
            "mapping, hazard monitoring, compliance analytics. It's slower going than the "
            "two smaller tools, partly because it's bigger, and partly because I keep "
            "learning things from quick-sitrep's real usage that change how I want to build "
            "the bigger system. That's probably how it should go."
        ),
        "featured_image_url": None,
        "published_at": datetime(2026, 9, 22, 0, 0, 0, tzinfo=dt_timezone.utc),
        "is_published": True,
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
            "--extras-only", action="store_true",
            help="Only insert missing work_experience / blog_post rows for the existing profile.",
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

    def seed_extras(self, dry_run):
        """Add work_experience / blog_post rows that aren't there yet. Safe to rerun."""
        profile = Profile.objects.filter(user__email=EMAIL).first()
        if profile is None:
            raise CommandError(f"No profile found for {EMAIL}; run seed_data (without flags) first.")

        added = {"work_experience": 0, "blog_post": 0}
        with transaction.atomic():
            for data in EXPERIENCE:
                exists = WorkExperience.objects.filter(
                    profile=profile,
                    company_name=data["company_name"],
                    position=data["position"],
                ).exists()
                if exists:
                    continue
                WorkExperience.objects.create(profile=profile, **data)
                added["work_experience"] += 1

            for data in BLOG_POSTS:
                if BlogPost.objects.filter(slug=data["slug"]).exists():
                    continue
                BlogPost.objects.create(profile=profile, **data)
                added["blog_post"] += 1

            if dry_run:
                transaction.set_rollback(True)
        label = "Dry run (rolled back)" if dry_run else "Seeded"
        self.stdout.write(self.style.SUCCESS(
            f"{label}: work_experience rows added={added['work_experience']}, "
            f"blog_post rows added={added['blog_post']}"
        ))

    def handle(self, *args, dry_run=False, media_only=False, extras_only=False, **options):
        if media_only:
            return self.seed_media(dry_run)
        if extras_only:
            return self.seed_extras(dry_run)
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
            for data in EXPERIENCE:
                WorkExperience.objects.create(profile=profile, **data)
            for data in BLOG_POSTS:
                BlogPost.objects.create(profile=profile, **data)

            summary = (
                f"user={Users.objects.count()} profile={Profile.objects.count()} "
                f"education={Education.objects.count()} skills={Skills.objects.count()} "
                f"projects={Project.objects.count()} tags={ProjectTag.objects.count()} "
                f"media={ProjectMedia.objects.count()} "
                f"experience={WorkExperience.objects.count()} blog_posts={BlogPost.objects.count()}"
            )
            if dry_run:
                transaction.set_rollback(True)
                self.stdout.write(self.style.WARNING(f"Dry run (rolled back): {summary}"))
                return

        self.stdout.write(self.style.SUCCESS(f"Seeded: {summary}"))
