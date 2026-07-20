from django.db import models


class ResumeTemplate(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    preview_image = models.ImageField(upload_to='template_previews/', blank=True, null=True)
    html_file = models.CharField(max_length=200, help_text='Path to the template HTML file')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Resume Template'
        verbose_name_plural = 'Resume Templates'
        ordering = ['name']
