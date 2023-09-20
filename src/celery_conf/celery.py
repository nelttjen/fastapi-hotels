from celery import Celery

from src.config import redis_settings

celery_app = Celery(
    __name__,
    broker=redis_settings.CELERY_BROKER_URL,
    backend=redis_settings.CELERY_RESULT_BACKEND,
    include=[
        'src.celery_conf.tasks.images',
        'src.celery_conf.tasks.emails',
    ],
)
