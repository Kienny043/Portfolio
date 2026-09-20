from django.conf import settings
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.http import Http404, HttpResponse
from django.utils import timezone
from django.views.decorators.http import require_safe
from rest_framework import status, viewsets
from rest_framework.exceptions import NotFound
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from .models import (
    Analytics,
    BlogPost,
    Education,
    Profile,
    Project,
    Skills,
    Testimonial,
    WorkExperience,
)
from .serializers import (
    BlogPostDetailSerializer,
    BlogPostListSerializer,
    ContactInquirySerializer,
    EducationSerializer,
    ProfileSerializer,
    ProjectSerializer,
    SkillSerializer,
    TestimonialSerializer,
    WorkExperienceSerializer,
)


def public_profiles():
    return Profile.objects.filter(is_public=True)


def get_owner_profile():
    """The portfolio owner: the first public profile."""
    profile = public_profiles().order_by("profile_id").first()
    if profile is None:
        raise NotFound("No public profile found.")
    return profile


class HealthView(APIView):
    """Lightweight liveness check for Render. Deliberately doesn't touch the database."""

    def get(self, request):
        return Response({"status": "ok"})


class ProfileViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProfileSerializer

    def get_queryset(self):
        return public_profiles().order_by("profile_id")


class OwnedReadOnlyViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only rows belonging to a public profile."""

    model = None
    ordering = ()

    def get_queryset(self):
        return self.model.objects.filter(profile__is_public=True).order_by(*self.ordering)


class EducationViewSet(OwnedReadOnlyViewSet):
    model = Education
    serializer_class = EducationSerializer
    ordering = ("-end_date", "-start_date", "education_id")


class ExperienceViewSet(OwnedReadOnlyViewSet):
    model = WorkExperience
    serializer_class = WorkExperienceSerializer
    ordering = ("-is_current", "-start_date", "experience_id")


class SkillViewSet(OwnedReadOnlyViewSet):
    model = Skills
    serializer_class = SkillSerializer
    ordering = ("category", "skill_id")


class ProjectViewSet(OwnedReadOnlyViewSet):
    model = Project
    serializer_class = ProjectSerializer
    ordering = ("display_order", "project_id")

    def get_queryset(self):
        return super().get_queryset().prefetch_related("projectmedia_set", "projecttag_set")


class TestimonialViewSet(OwnedReadOnlyViewSet):
    model = Testimonial
    serializer_class = TestimonialSerializer
    ordering = ("-date_received", "testimonial_id")


class BlogViewSet(OwnedReadOnlyViewSet):
    model = BlogPost
    ordering = ("-published_at", "post_id")
    lookup_field = "slug"

    def get_queryset(self):
        return super().get_queryset().filter(is_published=True)

    def get_serializer_class(self):
        return BlogPostDetailSerializer if self.action == "retrieve" else BlogPostListSerializer


class ContactView(CreateAPIView):
    serializer_class = ContactInquirySerializer
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "contact"

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.context["profile"] = get_owner_profile()
        serializer.save()
        # Don't echo the row back; the client only needs confirmation.
        return Response({"detail": "Message sent."}, status=status.HTTP_201_CREATED)


class AnalyticsView(APIView):
    """POST logs one visit as a row (viewer_count=1, visited_time=now)."""

    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "analytics"

    def post(self, request):
        Analytics.objects.create(
            profile=get_owner_profile(), viewer_count=1, visited_time=timezone.now()
        )
        return Response(status=status.HTTP_201_CREATED)


class AnalyticsCountView(APIView):
    def get(self, request):
        total = Analytics.objects.aggregate(total=Coalesce(Sum("viewer_count"), 0))["total"]
        return Response({"count": total})


@require_safe
def spa_index(request, path=""):
    """Catch-all for non-/api/ routes: return the React app's index.html so a refresh
    or deep link on any client-side path still loads it. Paths that look like files
    (have an extension) that WhiteNoise didn't already serve are real 404s, not the app."""
    if "." in path.rsplit("/", 1)[-1]:
        raise Http404
    for base in (settings.STATIC_ROOT, settings.FRONTEND_DIST):
        index = base / "index.html"
        if index.is_file():
            return HttpResponse(index.read_bytes(), content_type="text/html; charset=utf-8")
    raise Http404("Frontend not built. Run `npm run build` in frontend/.")
