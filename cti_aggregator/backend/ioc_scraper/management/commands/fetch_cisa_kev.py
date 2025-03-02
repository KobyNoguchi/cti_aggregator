from django.core.management.base import BaseCommand
from ioc_scraper.tasks import fetch_cisa_vulnerabilities

class Command(BaseCommand):
    help = 'Fetches CISA KEV vulnerability data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting CISA KEV data fetch...'))
        result = fetch_cisa_vulnerabilities()
        self.stdout.write(self.style.SUCCESS(f'Completed CISA KEV data fetch: {result}')) 