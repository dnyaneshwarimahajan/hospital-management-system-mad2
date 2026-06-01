from celery import Celery
from datetime import timedelta

import os

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

celery = Celery(
    'tasks',
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=['backend_jobs.task']
)

# celery = Celery('tasks',broker='redis://localhost:6379/0',
#                 backend='redis://localhost:6379/1',
#                 include=['backend_jobs.task'])

celery.conf.update(timezone='Asia/Kolkata', enable_utc=False, worker_pool='solo')

celery.conf.beat_schedule = {
    'send-daily-reminders': {
        'task': 'backend_jobs.task.send_daily_reminders',
        'schedule': timedelta(minutes=1),
    },
    'send-monthly-reports': {
        'task': 'backend_jobs.task.send_monthly_reports',
        'schedule': timedelta(minutes=2),   #crontab for production 
    },
}