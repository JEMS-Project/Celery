from celery import Celery
import redis
import json
import ssl
import certifi
from app.core.config import settings

# Configure Celery
app = Celery('celery_worker',
             broker=settings.UPSTASH_REDIS_URL,
             backend=settings.UPSTASH_REDIS_URL,
             broker_connection_retry_on_startup=True)

# SSL Configuration
app.conf.update(
    broker_use_ssl={
        'ssl_cert_reqs': ssl.CERT_REQUIRED,
        'ssl_ca_certs': certifi.where(),
    },
    redis_backend_use_ssl={
        'ssl_cert_reqs': ssl.CERT_REQUIRED,
        'ssl_ca_certs': certifi.where(),
    },
    task_default_queue=settings.REDIS_TASKS_QUEUE
)

# Redis client configuration
redis_client = redis.Redis.from_url(
    settings.UPSTASH_REDIS_URL,
    decode_responses=True
)

@app.task(name='worker.process_job_task')
def process_job_task(task_data):
    """Process job scraping task"""
    # To be implemented with actual job scraping logic
    print(f"Processing job task: {task_data}")
    return f"Completed: {task_data}"

def check_redis_queue():
    """Check Redis queue and process tasks"""
    while True:
        task_data = redis_client.blpop('task_queue', timeout=5)
        if task_data:
            task_json = task_data[1]
            task = json.loads(task_json)
            process_job_task.delay(task['data'])
