from celery import Celery
from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "chat_worker",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,
    worker_prefetch_multiplier=1,
)

@celery_app.task(name="app.worker.send_push_notification")
def send_push_notification(user_id: str, title: str, body: str, data: dict = None):
    # Placeholder for actual push notification logic (FCM/APNS)
    return {"status": "success", "user": user_id}

@celery_app.task(name="app.worker.process_offline_events")
def process_offline_events(user_id: str):
    # Placeholder for syncing events when user reconnects
    return {"status": "success", "user": user_id}
