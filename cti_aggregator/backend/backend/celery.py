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
}
