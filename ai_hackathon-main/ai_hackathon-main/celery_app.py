from celery import Celery
import os
from dotenv import load_dotenv

load_dotenv()

# Get Redis URL from environment (Render provides REDIS_URL)
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Initialize Celery
celery_app = Celery(
    "aikosh_worker",
    broker=redis_url,
    backend=redis_url
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # Stability settings
    worker_concurrency=int(os.getenv("WORKER_CONCURRENCY", 2)),
    task_time_limit=300, # 5 minutes hard limit
    task_soft_time_limit=240, 
)

# Import tasks so they are registered
import services.tasks
