import uuid
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('job_match', '0002_alter_skillgapanalysis_resume'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AnalysisTask',
            fields=[
                ('id', models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, serialize=False)),
                ('status', models.CharField(
                    choices=[('pending', 'Pending'), ('running', 'Running'), ('done', 'Done'), ('error', 'Error')],
                    db_index=True, default='pending', max_length=10,
                )),
                ('step', models.CharField(blank=True, max_length=120)),
                ('progress', models.PositiveSmallIntegerField(default=0)),
                ('payload', models.JSONField(default=dict)),
                ('analysis_id', models.IntegerField(blank=True, null=True)),
                ('error', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='analysis_tasks',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={'ordering': ['-created_at']},
        ),
    ]
