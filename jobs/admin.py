from django.contrib import admin
from .models import Employer, Job


@admin.register(Employer)
class EmployerAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'email', 'phone', 'trust_score', 'is_verified']
    search_fields = ['company_name', 'email']
    list_filter = ['is_verified']


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['title', 'employer', 'location', 'salary_range', 'trust_score', 'status', 'source', 'created_at']
    search_fields = ['title', 'employer__company_name', 'location']
    list_filter = ['status', 'source', 'employment_type', 'is_remote']
    readonly_fields = ['trust_score', 'verification_details', 'created_at', 'updated_at']
