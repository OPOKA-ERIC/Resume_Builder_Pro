import logging
from datetime import timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from django.conf import settings
from django.db import transaction
from django.utils import timezone

logger = logging.getLogger(__name__)

AGGREGATION_INTERVAL_SECONDS = 60

_scheduler = None


def run_aggregation():
    from .aggregator import JobAggregator
    from .models import AggregationState

    try:
        with transaction.atomic():
            state = AggregationState.objects.select_for_update().filter(key='aggregation').first()
            if state is None:
                state = AggregationState.objects.create(
                    key='aggregation',
                    last_run=timezone.now() - timedelta(days=1),
                )
            if timezone.now() - state.last_run < timedelta(seconds=AGGREGATION_INTERVAL_SECONDS):
                logger.info('Skipping scheduled aggregation: last run was under %s seconds ago',
                            AGGREGATION_INTERVAL_SECONDS)
                return
            state.last_run = timezone.now()
            state.save(update_fields=['last_run'])
        logger.info('Starting scheduled job aggregation...')
        results = JobAggregator().aggregate_all()
        logger.info('Scheduled aggregation complete: %s new jobs', results.get('total', 0))
    except Exception:
        logger.exception('Scheduled job aggregation failed')


def start_scheduler():
    global _scheduler
    if _scheduler is not None:
        return
    scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)
    scheduler.add_job(
        run_aggregation,
        IntervalTrigger(seconds=AGGREGATION_INTERVAL_SECONDS),
        id='job_aggregation',
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )
    scheduler.start()
    _scheduler = scheduler
    logger.info('Job aggregation scheduler started (every %s seconds)', AGGREGATION_INTERVAL_SECONDS)
