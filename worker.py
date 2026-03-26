# worker.py
from celery import Celery
from dotenv import load_dotenv
import os

load_dotenv()

# Use REDIS_URL env variable
# On localhost it falls back to localhost:6379
redis_url = os.getenv("REDIS_URL", "redis://default:ZJtJOdQdotAOwpdDyNyaebdtGIjXerNE@ballast.proxy.rlwy.net:51292")

celery_app = Celery(
    "plutonity",
    broker=redis_url,
    backend=redis_url,
    include=["app.tasks"]
)

celery_app.conf.update(
    task_soft_time_limit=120,
    task_time_limit=180,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_concurrency=2,
    result_expires=86400,
)
