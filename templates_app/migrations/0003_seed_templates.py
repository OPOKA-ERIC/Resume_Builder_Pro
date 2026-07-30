from django.db import migrations


def create_templates(apps, schema_editor):
    ResumeTemplate = apps.get_model('templates_app', 'ResumeTemplate')
    templates = [
        {
            'name': 'Professional',
            'description': 'A clean, traditional resume layout with serif fonts and a formal structure. Best for corporate, finance, and academic positions.',
            'html_file': 'pdf/resume_professional.html',
            'is_active': True,
        },
        {
            'name': 'Modern',
            'description': 'A contemporary design with a sidebar layout, sans-serif fonts, and a blue accent color. Ideal for tech, creative, and startup roles.',
            'html_file': 'pdf/resume_modern.html',
            'is_active': True,
        },
        {
            'name': 'Creative',
            'description': 'A bold, colorful design with a gradient header and pill-shaped badges. Perfect for designers, marketers, and creative professionals.',
            'html_file': 'pdf/resume_creative.html',
            'is_active': True,
        },
    ]
    for t in templates:
        ResumeTemplate.objects.get_or_create(
            name=t['name'],
            defaults=t,
        )


def reverse_templates(apps, schema_editor):
    ResumeTemplate = apps.get_model('templates_app', 'ResumeTemplate')
    ResumeTemplate.objects.filter(name__in=['Professional', 'Modern', 'Creative']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('templates_app', '0002_add_template_theming_fields'),
    ]

    operations = [
        migrations.RunPython(create_templates, reverse_templates),
    ]
