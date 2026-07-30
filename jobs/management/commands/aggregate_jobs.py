from django.core.management.base import BaseCommand
from jobs.aggregator import JobAggregator


class Command(BaseCommand):
    help = 'Aggregate jobs from external APIs'

    def handle(self, *args, **options):
        self.stdout.write('Starting job aggregation...')
        aggregator = JobAggregator()
        results = aggregator.aggregate_all()
        total = results.get('total', 0)
        self.stdout.write(self.style.SUCCESS(f'Aggregation complete: {total} new jobs added'))
