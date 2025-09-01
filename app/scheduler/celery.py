from celery import Celery
from celery.schedules import crontab
import os


BROKER_URL = os.getenv("CELERY_BROKER_URL")
celery = Celery(broker=BROKER_URL)

celery.autodiscover_tasks(["app.scheduler.tasks"])


celery.conf.beat_schedule = {
    "request-and-store-rates-data": {
        "task": "app.scheduler.tasks.request_and_store_rates_data",
        "schedule": crontab(hour=13),
    },
}

celery.conf.timezone = os.getenv("TIMEZONE")
