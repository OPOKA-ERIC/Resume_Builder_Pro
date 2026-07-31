from django.db import models
import json


class ResumeTemplate(models.Model):
    ARCHETYPE_CHOICES = [
        ('A', 'Sidebar Left'),
        ('B', 'Header Banner'),
        ('C', 'Single Column'),
        ('D', 'Split Balanced'),
        ('E', 'Card/Panel'),
        ('F', 'Photo Forward'),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    preview_image = models.ImageField(upload_to='template_previews/', blank=True, null=True)
    html_file = models.CharField(max_length=200, help_text='Path to the template HTML file (for legacy templates)')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # New fields for the theming system
    archetype = models.CharField(max_length=1, choices=ARCHETYPE_CHOICES, blank=True, null=True,
                                  help_text='Layout archetype (A-F) for new templates')
    skin_file = models.CharField(max_length=200, blank=True, null=True,
                                  help_text='Path to the skin template (e.g., themes/skins/nebula.html)')
    tags = models.JSONField(default=list, blank=True,
                             help_text='Tags for filtering: modern, simple, with_photo, professional')
    swatches = models.JSONField(default=list, blank=True,
                                 help_text='Preset accent colors as hex codes')
    supports_photo = models.BooleanField(default=False,
                                          help_text='Whether this template supports profile photos')
    supports_monochrome = models.BooleanField(default=False,
                                               help_text='Whether this template supports monochrome mode')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Resume Template'
        verbose_name_plural = 'Resume Templates'
        ordering = ['name']

    def get_archetype_path(self):
        """Return the full template path for this skin."""
        if self.skin_file:
            return f'resumes/themes/{self.skin_file}'
        return self.html_file

    def get_default_swatches(self):
        """Return swatches with a default if empty."""
        if self.swatches:
            return self.swatches
        return ['#1d4ed8', '#059669', '#d97706', '#dc2626', '#9333ea']
