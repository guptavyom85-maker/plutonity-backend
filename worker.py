# worker.py
from celery import Celery
from dotenv import load_dotenv
import os

load_dotenv()

celery_app = Celery(
    "plutonity",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
    include=["app.tasks"]       # ← THIS is what was missing
)

celery_app.conf.update(
    task_soft_time_limit=120,
    task_time_limit=180,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_concurrency=2,
    result_expires=86400,
)