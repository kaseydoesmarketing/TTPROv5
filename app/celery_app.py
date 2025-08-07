from celery import Celery
from .config import settings

celery_app = Celery(
    "titletesterpro",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

celery_app.conf.beat_schedule = {
    "rotate-titles": {
        "task": "app.tasks.rotate_titles",
        "schedule": 60.0,  # Run every minute to check for rotations
    },
    "cleanup-completed-tests": {
        "task": "app.tasks.cleanup_completed_tests",
        "schedule": 3600.0,  # Run every hour
    },
}
