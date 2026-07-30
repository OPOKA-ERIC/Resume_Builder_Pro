from django.contrib import admin
from .models import JobDescription, SkillGapAnalysis


@admin.register(JobDescription)
class JobDescriptionAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('title', 'company', 'raw_text')


@admin.register(SkillGapAnalysis)
class SkillGapAnalysisAdmin(admin.ModelAdmin):
    list_display = ('job', 'resume', 'overall_score', 'created_at')
    list_filter = ('overall_score', 'created_at')
    search_fields = ('job__title', 'resume__title')
