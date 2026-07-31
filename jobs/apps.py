import os

from django.apps import AppConfig
from django.db.backends.signals import connection_created


def _enable_sqlite_concurrency(sender, connection, **kwargs):
    if connection.vendor == 'sqlite':
        try:
            with connection.cursor() as cursor:
                cursor.execute('PRAGMA journal_mode=WAL;')
                cursor.execute('PRAGMA busy_timeout=20000;')
        except Exception:
            pass


class JobsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'jobs'
    verbose_name = 'Jobs'

    def ready(self):
        connection_created.connect(_enable_sqlite_concurrency, dispatch_uid='jobs_enable_sqlite_concurrency')
        if os.environ.get('RUN_MAIN') == 'true':
            from .scheduler import start_scheduler
            start_scheduler()
