import os
from celery import Celery
from celery.schedules import crontab
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
)
logger = logging.getLogger(__name__)

# Set Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

# Initialize Celery app
app = Celery("backend")
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks from Django apps
app.autodiscover_tasks()

# Configure Celery
app.conf.update(
    # Broker settings
    broker_connection_retry=True,
    broker_connection_retry_on_startup=True,
    broker_connection_max_retries=5,
    
    # Result backend settings
    result_expires=60 * 60 * 24,  # Results expire after 1 day
    
    # Task settings
    task_acks_late=True,           # Tasks are acknowledged after execution (better for retries)
    task_reject_on_worker_lost=True, # Reject tasks if worker is lost
    task_time_limit=60 * 30,       # 30 minute hard time limit
    task_soft_time_limit=60 * 25,  # 25 minute soft time limit (warning)
    
    # Worker settings
    worker_prefetch_multiplier=1,  # Prefetch only one task at a time (better for long-running tasks)
    worker_max_tasks_per_child=200, # Restart worker after 200 tasks
    worker_hijack_root_logger=False, # Don't hijack the root logger
    
    # Logging
    worker_log_format='[%(asctime)s: %(levelname)s/%(processName)s] %(message)s',
    worker_task_log_format='[%(asctime)s: %(levelname)s/%(processName)s] [%(task_name)s(%(task_id)s)] %(message)s',
)

# Task scheduling
app.conf.beat_schedule = {
    # CISA KEV daily updates (midnight)
    "fetch-cisa-kev-daily": {
        "task": "ioc_scraper.tasks.fetch_cisa_vulnerabilities",
        "schedule": crontab(hour=0, minute=0),
        "options": {
            "expires": 60 * 60 * 3,  # Task expires after 3 hours
            "retry": True,
            "retry_policy": {
                "max_retries": 3,
                "interval_start": 60,
                "interval_step": 60,
                "interval_max": 300,
            },
        },
    },
    
    # Intelligence articles every hour (changed from every 4 hours)
    "fetch-intelligence-articles": {
        "task": "ioc_scraper.tasks.fetch_all_intelligence",
        "schedule": crontab(hour='*', minute=0),  # Every hour
        "options": {
            "expires": 60 * 60 * 3,  # Task expires after 3 hours
            "retry": True,
        },
    },
    
    # CrowdStrike intelligence every 6 hours
    'fetch-crowdstrike-intel': {
        'task': 'ioc_scraper.tasks.fetch_crowdstrike_intel',
        'schedule': crontab(hour='*/6', minute=30),  # Every 6 hours at half past
        "options": {
            "expires": 60 * 60 * 5,  # Task expires after 5 hours
            "retry": True,
        },
    },
    
    # Tailored intelligence once a day (morning)
    'update-tailored-intelligence': {
        'task': 'ioc_scraper.tasks.update_tailored_intelligence',
        'schedule': crontab(hour=6, minute=0),  # Daily at 6 AM
        "options": {
            "expires": 60 * 60 * 12,  # Task expires after 12 hours
            "retry": True, 
        },
    },
    
    # Daily system health check and cleanup
    'system-health-check': {
        'task': 'ioc_scraper.tasks.system_health_check',
        'schedule': crontab(hour=5, minute=0),  # Daily at 5 AM
        "options": {
            "expires": 60 * 60 * 2,  # Task expires after 2 hours
        },
    },
}

@app.task(bind=True)
def debug_task(self):
    """Task to verify that Celery is working correctly."""
    logger.info(f'Request: {self.request!r}')
    return "Celery is working correctly"
