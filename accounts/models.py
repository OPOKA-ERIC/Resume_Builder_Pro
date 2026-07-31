from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    website = models.URLField(blank=True, help_text='Personal website URL')
    city = models.CharField(max_length=100, blank=True)
    skills = models.TextField(
        blank=True,
        help_text='Comma-separated skills that will be auto-added to new job resumes.',
    )
    career_data = models.JSONField(
        default=dict, blank=True,
        help_text='Structured career biodata (education, experience, projects, certifications, languages) used to pre-fill job resumes.',
    )
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"Profile of {self.user.username}"

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
