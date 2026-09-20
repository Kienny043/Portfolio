from django.urls import path
from rest_framework.routers import SimpleRouter

from . import views

router = SimpleRouter()
router.register("profile", views.ProfileViewSet, basename="profile")
router.register("education", views.EducationViewSet, basename="education")
router.register("experience", views.ExperienceViewSet, basename="experience")
router.register("skills", views.SkillViewSet, basename="skills")
router.register("projects", views.ProjectViewSet, basename="projects")
router.register("testimonials", views.TestimonialViewSet, basename="testimonials")
router.register("blog", views.BlogViewSet, basename="blog")

urlpatterns = [
    path("health/", views.HealthView.as_view()),
    path("contact/", views.ContactView.as_view()),
    path("analytics/", views.AnalyticsView.as_view()),
    path("analytics/count/", views.AnalyticsCountView.as_view()),
    *router.urls,
]
