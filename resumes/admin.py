from django.contrib import admin
from .models import (
    Resume, Education, Experience, Skill,
    Project, Certification, Language, Reference
)


class EducationInline(admin.TabularInline):
    model = Education
    extra = 0


class ExperienceInline(admin.TabularInline):
    model = Experience
    extra = 0


class SkillInline(admin.TabularInline):
    model = Skill
    extra = 0


class ProjectInline(admin.TabularInline):
    model = Project
    extra = 0


class CertificationInline(admin.TabularInline):
    model = Certification
    extra = 0


class LanguageInline(admin.TabularInline):
    model = Language
    extra = 0


class ReferenceInline(admin.TabularInline):
    model = Reference
    extra = 0


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'template', 'created_at', 'updated_at']
    list_filter = ['user', 'template']
    search_fields = ['title', 'user__username']
    inlines = [
        EducationInline, ExperienceInline, SkillInline,
        ProjectInline, CertificationInline, LanguageInline, ReferenceInline,
    ]


admin.site.register(Education)
admin.site.register(Experience)
admin.site.register(Skill)
admin.site.register(Project)
admin.site.register(Certification)
admin.site.register(Language)
admin.site.register(Reference)
