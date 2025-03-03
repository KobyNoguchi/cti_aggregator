import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

app = Celery("backend")
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks from Django apps
app.autodiscover_tasks()

# Add broker_connection_retry_on_startup setting to address deprecation warning
app.conf.broker_connection_retry_on_startup = True

app.conf.beat_schedule={
    "fetch-cisa-kev-daily": {
        "task": "ioc_scraper.tasks.fetch_cisa_vulnerabilities",
        "schedule": crontab(hour=0, minute=0),
    },
    "fetch-intelligence-articles-hourly": {
        "task": "ioc_scraper.tasks.fetch_all_intelligence",
        "schedule": crontab(minute=0),  # Run every hour at minute 0
    },
    'fetch-crowdstrike-intel-every-hour': {
        'task': 'ioc_scraper.tasks.fetch_crowdstrike_intel',
        'schedule': 3600.0,  # Every hour
    },
    'update-tailored-intelligence-every-day': {
        'task': 'ioc_scraper.tasks.update_tailored_intelligence',
        'schedule': 86400.0,  # Every 24 hours (in seconds)
        'args': (),
    },
}
