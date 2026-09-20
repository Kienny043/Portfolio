# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Analytics(models.Model):
    analytics_id = models.AutoField(primary_key=True)
    profile = models.ForeignKey('Profile', models.DO_NOTHING)
    viewer_count = models.IntegerField(blank=True, null=True)
    visited_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'analytics'


class BlogPost(models.Model):
    post_id = models.AutoField(primary_key=True)
    profile = models.ForeignKey('Profile', models.DO_NOTHING)
    title = models.TextField()
    slug = models.TextField(unique=True)
    excerpt = models.TextField(blank=True, null=True)
    content = models.TextField()
    featured_image_url = models.TextField(blank=True, null=True)
    published_at = models.DateTimeField(blank=True, null=True)
    is_published = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'blog_post'


class ContactInquiry(models.Model):
    inquiry_id = models.AutoField(primary_key=True)
    profile = models.ForeignKey('Profile', models.DO_NOTHING)
    sender_name = models.TextField()
    sender_email = models.TextField()
    subject = models.TextField(blank=True, null=True)
    message = models.TextField()
    sent_at = models.DateTimeField(blank=True, null=True)
    is_read = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'contact_inquiry'


class Education(models.Model):
    education_id = models.AutoField(primary_key=True)
    profile = models.ForeignKey('Profile', models.DO_NOTHING)
    institution = models.TextField()
    degree = models.TextField(blank=True, null=True)
    field_of_study = models.TextField(blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    grade = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'education'


class Profile(models.Model):
    profile_id = models.AutoField(primary_key=True)
    user = models.OneToOneField('Users', models.DO_NOTHING)
    lastname = models.TextField()
    firstname = models.TextField()
    middlename = models.TextField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    is_public = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'profile'


class Project(models.Model):
    project_id = models.AutoField(primary_key=True)
    profile = models.ForeignKey(Profile, models.DO_NOTHING)
    title = models.TextField()
    description = models.TextField(blank=True, null=True)
    demo_url = models.TextField(blank=True, null=True)
    is_featured = models.BooleanField(blank=True, null=True)
    display_order = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'project'


class ProjectMedia(models.Model):
    project_media_id = models.AutoField(primary_key=True)
    project = models.ForeignKey(Project, models.DO_NOTHING)
    media_url = models.TextField()
    display_order = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'project_media'


class ProjectTag(models.Model):
    tag_id = models.AutoField(primary_key=True)
    project = models.ForeignKey(Project, models.DO_NOTHING)
    tag_name = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'project_tag'


class Skills(models.Model):
    skill_id = models.AutoField(primary_key=True)
    profile = models.ForeignKey(Profile, models.DO_NOTHING)
    category = models.TextField(blank=True, null=True)
    year_acquired = models.IntegerField(blank=True, null=True)
    certification = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'skills'


class Testimonial(models.Model):
    testimonial_id = models.AutoField(primary_key=True)
    profile = models.ForeignKey(Profile, models.DO_NOTHING)
    client_name = models.TextField()
    client_company = models.TextField(blank=True, null=True)
    content = models.TextField()
    rating = models.IntegerField(blank=True, null=True)
    date_received = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'testimonial'


class Users(models.Model):
    user_id = models.AutoField(primary_key=True)
    email = models.TextField(unique=True)
    password = models.TextField()
    role = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'users'


class WorkExperience(models.Model):
    experience_id = models.AutoField(primary_key=True)
    profile = models.ForeignKey(Profile, models.DO_NOTHING)
    company_name = models.TextField()
    position = models.TextField()
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    is_current = models.BooleanField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'work_experience'
