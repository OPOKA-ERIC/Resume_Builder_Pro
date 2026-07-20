from django.db import models
from django.contrib.auth.models import User
from templates_app.models import ResumeTemplate


class Resume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resumes')
    title = models.CharField(max_length=200)
    template = models.ForeignKey(
        ResumeTemplate, on_delete=models.SET_NULL, null=True, blank=True, related_name='resumes'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Resume'
        verbose_name_plural = 'Resumes'
        ordering = ['-updated_at']


class Education(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='educations')
    institution = models.CharField(max_length=200)
    qualification = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.qualification} - {self.institution}"

    class Meta:
        verbose_name = 'Education'
        verbose_name_plural = 'Education'


class Experience(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='experiences')
    company = models.CharField(max_length=200)
    role = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.role} at {self.company}"

    class Meta:
        verbose_name = 'Experience'
        verbose_name_plural = 'Experiences'


class Skill(models.Model):
    PROFICIENCY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert'),
    ]

    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='skills')
    name = models.CharField(max_length=100)
    proficiency_level = models.CharField(max_length=20, choices=PROFICIENCY_CHOICES, default='intermediate')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Skill'
        verbose_name_plural = 'Skills'


class Project(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='projects')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    link = models.URLField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'


class Certification(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='certifications')
    title = models.CharField(max_length=200)
    issuer = models.CharField(max_length=200)
    date_awarded = models.DateField()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Certification'
        verbose_name_plural = 'Certifications'


class Language(models.Model):
    PROFICIENCY_CHOICES = [
        ('basic', 'Basic'),
        ('conversational', 'Conversational'),
        ('fluent', 'Fluent'),
        ('native', 'Native'),
    ]

    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='languages')
    name = models.CharField(max_length=100)
    proficiency_level = models.CharField(max_length=20, choices=PROFICIENCY_CHOICES, default='fluent')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Language'
        verbose_name_plural = 'Languages'


class Reference(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='references')
    name = models.CharField(max_length=200)
    relationship = models.CharField(max_length=200)
    contact = models.CharField(max_length=200)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Reference'
        verbose_name_plural = 'References'
