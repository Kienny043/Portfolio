from django.utils import timezone
from rest_framework import serializers

from .models import (
    Analytics,
    BlogPost,
    ContactInquiry,
    Education,
    Profile,
    Project,
    ProjectMedia,
    ProjectTag,
    Skills,
    Testimonial,
    WorkExperience,
)

# Fields that must never appear in any API output.
FORBIDDEN_FIELDS = {"password", "user", "user_id"}


class SafeModelSerializer(serializers.ModelSerializer):
    """Base serializer: refuses to build its fields if it would expose the users
    table or its password. Every serializer in this module inherits it, and each
    uses an explicit allow-list of fields (never `exclude`/`__all__`)."""

    def get_fields(self):
        fields = super().get_fields()
        leaked = FORBIDDEN_FIELDS & set(fields)
        if leaked:
            raise AssertionError(
                f"{type(self).__name__} exposes forbidden field(s): {sorted(leaked)}"
            )
        return fields


class ProfileSerializer(SafeModelSerializer):
    class Meta:
        model = Profile
        # `user` (FK to users, which holds `password`) is deliberately absent.
        fields = ["profile_id", "firstname", "middlename", "lastname", "bio"]


class EducationSerializer(SafeModelSerializer):
    class Meta:
        model = Education
        fields = [
            "education_id", "institution", "degree", "field_of_study",
            "start_date", "end_date", "grade",
        ]


class WorkExperienceSerializer(SafeModelSerializer):
    class Meta:
        model = WorkExperience
        fields = [
            "experience_id", "company_name", "position", "start_date",
            "end_date", "is_current", "description",
        ]


class SkillSerializer(SafeModelSerializer):
    class Meta:
        model = Skills
        fields = ["skill_id", "category", "year_acquired", "certification"]


class ProjectMediaSerializer(SafeModelSerializer):
    class Meta:
        model = ProjectMedia
        fields = ["project_media_id", "media_url", "display_order"]


class ProjectTagSerializer(SafeModelSerializer):
    class Meta:
        model = ProjectTag
        fields = ["tag_id", "tag_name"]


class ProjectSerializer(SafeModelSerializer):
    media = ProjectMediaSerializer(source="projectmedia_set", many=True, read_only=True)
    tags = ProjectTagSerializer(source="projecttag_set", many=True, read_only=True)

    class Meta:
        model = Project
        fields = [
            "project_id", "title", "description", "demo_url",
            "is_featured", "display_order", "media", "tags",
        ]


class TestimonialSerializer(SafeModelSerializer):
    class Meta:
        model = Testimonial
        fields = [
            "testimonial_id", "client_name", "client_company",
            "content", "rating", "date_received",
        ]


class BlogPostListSerializer(SafeModelSerializer):
    class Meta:
        model = BlogPost
        fields = ["post_id", "title", "slug", "excerpt", "featured_image_url", "published_at"]


class BlogPostDetailSerializer(BlogPostListSerializer):
    class Meta(BlogPostListSerializer.Meta):
        fields = BlogPostListSerializer.Meta.fields + ["content"]


class ContactInquirySerializer(SafeModelSerializer):
    """Input only; profile, sent_at and is_read are set server-side."""

    sender_name = serializers.CharField(max_length=200)
    sender_email = serializers.EmailField(max_length=254)
    subject = serializers.CharField(max_length=200, required=False, allow_blank=True)
    message = serializers.CharField(max_length=5000)

    class Meta:
        model = ContactInquiry
        fields = ["sender_name", "sender_email", "subject", "message"]

    def create(self, validated_data):
        return ContactInquiry.objects.create(
            profile=self.context["profile"],
            sent_at=timezone.now(),
            is_read=False,
            **validated_data,
        )
