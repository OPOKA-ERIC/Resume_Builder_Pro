import uuid
from django.db import models
from django.contrib.auth.models import User
from resumes.models import Resume


def generate_slug():
    return uuid.uuid4().hex[:12]


class Portfolio(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='portfolios')
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='portfolios')
    title = models.CharField(max_length=200, blank=True)
    slug = models.SlugField(unique=True, default=generate_slug, max_length=20)
    is_published = models.BooleanField(default=False)
    views = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Portfolio'
        verbose_name_plural = 'Portfolios'
        ordering = ['-updated_at']

    def __str__(self):
        return self.title or f"Portfolio of {self.resume.title}"

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('portfolio:manage', args=[self.id])

    def get_public_url(self):
        from django.urls import reverse
        return reverse('portfolio_public', args=[self.slug])

    def save(self, *args, **kwargs):
        if not self.title:
            self.title = f"Portfolio - {self.resume.title}"
        super().save(*args, **kwargs)
