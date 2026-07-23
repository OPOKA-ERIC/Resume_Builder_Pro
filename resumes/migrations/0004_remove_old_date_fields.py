from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("resumes", "0003_populate_year_fields"),
    ]

    operations = [
        migrations.RemoveField(model_name="education", name="start_date"),
        migrations.RemoveField(model_name="education", name="end_date"),
        migrations.RemoveField(model_name="experience", name="start_date"),
        migrations.RemoveField(model_name="experience", name="end_date"),
        migrations.RemoveField(model_name="certification", name="date_awarded"),
        migrations.AlterField(model_name="education", name="start_year", field=models.IntegerField()),
        migrations.AlterField(model_name="experience", name="start_year", field=models.IntegerField()),
        migrations.AlterField(model_name="certification", name="year_awarded", field=models.IntegerField()),
    ]
