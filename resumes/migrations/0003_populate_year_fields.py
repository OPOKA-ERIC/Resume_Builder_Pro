from django.db import migrations


def copy_dates_to_years(apps, schema_editor):
    Education = apps.get_model('resumes', 'Education')
    Experience = apps.get_model('resumes', 'Experience')
    Certification = apps.get_model('resumes', 'Certification')

    for edu in Education.objects.all():
        if edu.start_date:
            edu.start_year = edu.start_date.year
        if edu.end_date:
            edu.end_year = edu.end_date.year
        edu.save(update_fields=['start_year', 'end_year'])

    for exp in Experience.objects.all():
        if exp.start_date:
            exp.start_year = exp.start_date.year
        if exp.end_date:
            exp.end_year = exp.end_date.year
        exp.save(update_fields=['start_year', 'end_year'])

    for cert in Certification.objects.all():
        if cert.date_awarded:
            cert.year_awarded = cert.date_awarded.year
        cert.save(update_fields=['year_awarded'])


def reverse_copy(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("resumes", "0002_add_year_fields"),
    ]

    operations = [
        migrations.RunPython(copy_dates_to_years, reverse_copy),
    ]
