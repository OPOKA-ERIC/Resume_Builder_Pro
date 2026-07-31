import uuid
from django.db import models
from django.contrib.auth.models import User


class AnalysisTask(models.Model):
    """Lightweight async job queue backed by the DB."""
    STATUS_PENDING  = 'pending'
    STATUS_RUNNING  = 'running'
    STATUS_DONE     = 'done'
    STATUS_ERROR    = 'error'
    STATUS_CHOICES  = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_RUNNING, 'Running'),
        (STATUS_DONE,    'Done'),
        (STATUS_ERROR,   'Error'),
    ]

    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user        = models.ForeignKey(User, on_delete=models.CASCADE, related_name='analysis_tasks')
    status      = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING, db_index=True)
    step        = models.CharField(max_length=120, blank=True)
    progress    = models.PositiveSmallIntegerField(default=0)
    payload     = models.JSONField(default=dict)
    analysis_id = models.IntegerField(null=True, blank=True)
    error       = models.TextField(blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Task {self.id} [{self.status}]'


class JobDescription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_descriptions')
    title = models.CharField(max_length=200, blank=True)
    company = models.CharField(max_length=200, blank=True)
    location = models.CharField(max_length=200, blank=True)
    raw_text = models.TextField()
    source_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Job Description'
        verbose_name_plural = 'Job Descriptions'
        ordering = ['-created_at']

    def __str__(self):
        return self.title or f"Job #{self.id}"


class SkillGapAnalysis(models.Model):
    job = models.ForeignKey(JobDescription, on_delete=models.CASCADE, related_name='analyses')
    resume = models.ForeignKey('resumes.Resume', on_delete=models.SET_NULL, null=True, blank=True, related_name='gap_analyses')
    task = models.ForeignKey('AnalysisTask', on_delete=models.SET_NULL, null=True, blank=True, related_name='analyses')
    overall_score = models.FloatField()
    matched_skills = models.JSONField(default=list)
    missing_skills = models.JSONField(default=list)
    partial_skills = models.JSONField(default=list)
    recommendations = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Skill Gap Analysis'
        verbose_name_plural = 'Skill Gap Analyses'
        ordering = ['-created_at']

    def __str__(self):
        return f"Analysis #{self.id} — {self.overall_score:.0f}% match"


class JobPool(models.Model):
    """Caches the jobs found for a resume so re-runs re-score the SAME jobs."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_pools')
    resume = models.ForeignKey('resumes.Resume', on_delete=models.SET_NULL, null=True, blank=True, related_name='job_pools')
    fingerprint = models.CharField(max_length=64, blank=True, db_index=True, help_text='SHA-1 of resume text (for uploaded files)')
    jobs = models.ManyToManyField(JobDescription, related_name='pools', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Job Pool'
        verbose_name_plural = 'Job Pools'
        ordering = ['-updated_at']

    def __str__(self):
        return f"Pool for {self.resume or self.fingerprint[:8]} ({self.jobs.count()} jobs)"
