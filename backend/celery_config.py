import sys
import os
from celery import Celery
from celery.schedules import crontab

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

celery = Celery(
    'tasks',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/1',
    include=['task']
)

celery.conf.update(timezone='Asia/Kolkata', enable_utc=False, worker_pool='solo')

celery.conf.beat_schedule = {
    'send-daily-reminders': {
        'task': 'task.send_daily_reminders',
        'schedule': crontab(minute=1),           # runs every day at 8:00 AM
    },
    'send-monthly-reports': {
        'task': 'task.send_monthly_reports',
        'schedule': crontab( minute=2),  # runs 1st of every month at 6:00 AM
    },
}