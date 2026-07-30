from datetime import timedelta
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone


class Employer(models.Model):
    company_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=50, blank=True)
    website = models.URLField(blank=True)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='employer_logos/', blank=True)
    is_verified = models.BooleanField(default=False)
    trust_score = models.IntegerField(default=0)
    verification_details = models.JSONField(default=dict, blank=True)
    registered_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-trust_score', 'company_name']
        verbose_name = 'Employer'

    def __str__(self):
        return self.company_name


class Job(models.Model):
    EMPLOYMENT_TYPES = [
        ('full_time', 'Full-Time'),
        ('part_time', 'Part-Time'),
        ('contract', 'Contract'),
        ('temporary', 'Temporary'),
        ('internship', 'Internship'),
        ('freelance', 'Freelance'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('expired', 'Expired'),
    ]

    SOURCE_CHOICES = [
        ('employer', 'Employer Posted'),
        ('aggregated', 'Aggregated'),
        ('admin', 'Admin Added'),
    ]

    title = models.CharField(max_length=200)
    employer = models.ForeignKey(Employer, on_delete=models.CASCADE, related_name='jobs')
    description = models.TextField()
    description_original = models.TextField(blank=True, help_text='Original untranslated description')
    description_language = models.CharField(max_length=10, blank=True, help_text='Detected language code of original')
    requirements = models.TextField(blank=True)
    responsibilities = models.TextField(blank=True)
    location = models.CharField(max_length=200)
    is_remote = models.BooleanField(default=False)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    salary_min = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, default='USD')
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPES, default='full_time')
    category = models.CharField(max_length=100, blank=True, db_index=True)
    application_url = models.URLField(blank=True, help_text='External URL to apply (hidden behind paywall)')
    application_email = models.EmailField(blank=True, help_text='Email to send application (hidden behind paywall)')
    application_instructions = models.TextField(blank=True, help_text='Hidden behind paywall')

    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='employer')
    source_url = models.URLField(blank=True, help_text='Original URL if aggregated')
    source_id = models.CharField(max_length=200, blank=True, db_index=True, help_text='External ID from source API')

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    trust_score = models.IntegerField(default=0, help_text='0-100 score for scam detection')
    verification_details = models.JSONField(default=dict, blank=True)
    rejection_reason = models.TextField(blank=True)

    is_featured = models.BooleanField(default=False)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Who can see application details
    requires_resume = models.BooleanField(default=True)

    class Meta:
        ordering = ['-is_featured', '-trust_score', '-created_at']
        indexes = [
            models.Index(fields=['location']),
            models.Index(fields=['category']),
            models.Index(fields=['status', 'trust_score']),
        ]

    def __str__(self):
        return f"{self.title} at {self.employer.company_name}"

    @property
    def salary_range(self):
        if self.salary_min and self.salary_max:
            return f"{self.currency} {self.salary_min:,.0f} - {self.salary_max:,.0f}"
        elif self.salary_min:
            return f"From {self.currency} {self.salary_min:,.0f}"
        elif self.salary_max:
            return f"Up to {self.currency} {self.salary_max:,.0f}"
        return 'Negotiable'

    @property
    def time_since_posted(self):
        now = timezone.now()
        diff = now - self.created_at
        if diff < timedelta(minutes=1):
            return 'Just now'
        elif diff < timedelta(hours=1):
            mins = int(diff.total_seconds() // 60)
            return f'{mins} minute{"s" if mins != 1 else ""} ago'
        elif diff < timedelta(days=1):
            hours = int(diff.total_seconds() // 3600)
            return f'{hours} hour{"s" if hours != 1 else ""} ago'
        elif diff < timedelta(days=30):
            days = diff.days
            return f'{days} day{"s" if days != 1 else ""} ago'
        elif diff < timedelta(days=365):
            months = diff.days // 30
            return f'{months} month{"s" if months != 1 else ""} ago'
        else:
            years = diff.days // 365
            return f'{years} year{"s" if years != 1 else ""} ago'


class JobApplication(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_applications')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    resume = models.ForeignKey('resumes.Resume', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'job']

    def __str__(self):
        return f"{self.user.username} applied to {self.job.title}"
