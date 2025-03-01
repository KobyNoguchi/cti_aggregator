import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

app = Celery("backend")
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks from Django apps
app.autodiscover_tasks()


app.conf.beat_schedule={
    "fetch-cisa-kev-daily": {
        "task": "ioc_scraper.tasks.fetch_cisa_vulnerabilities",
        "schedule": crontab(hour=0, minute=0),
    },
    "fetch-intelligence-articles-daily": {
        "task": "ioc_scraper.tasks.fetch_all_intelligence",
        "schedule": crontab(hour=1, minute=0),  # Run at 1 AM to avoid conflicts
    },
    'scrape-cisa-every-hour': {
        'task': 'ioc_scraper.tasks.scrape_cisa_kev',
        'schedule': 3600.0,  # Every hour
    },
    'fetch-crowdstrike-intel-every-hour': {
        'task': 'ioc_scraper.tasks.fetch_crowdstrike_intel',
        'schedule': 3600.0,  # Every hour
    },
}
