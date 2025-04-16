'''
Keep the Worker Running
Leave this terminal open.
celery -A celery_client worker --loglevel=info --pool=solo

Run the Enqueue Script: In a new terminal
python enqueue_tasks.py

Run the Client: In another terminal
python celery_client.py
'''

from celery import Celery
import redis
import json
import ssl
import certifi
from app.core.config import settings

# Configure Celery with the properly formatted Redis URL
app = Celery('celery_client')

# Set configuration
app.conf.update(
    # Broker and Backend settings
    broker_url=settings.celery_broker_url,
    result_backend=settings.celery_broker_url,
    
    # SSL Configuration for both broker and backend
    broker_use_ssl={
        'ssl_cert_reqs': ssl.CERT_REQUIRED,
        'ssl_ca_certs': certifi.where(),
    },
    redis_backend_use_ssl={
        'ssl_cert_reqs': ssl.CERT_REQUIRED,
        'ssl_ca_certs': certifi.where(),
    },
    
    # Task settings
    task_track_started=True,
    task_ignore_result=False,
    result_expires=3600,
    task_default_queue=settings.REDIS_TASKS_QUEUE,
    broker_connection_retry_on_startup=True,
)

# Redis client for direct operations
redis_client = redis.Redis(**settings.redis_config)

@app.task(bind=True, name='celery_client.process_task')
def process_task(self, task_data):
    """Task processing function with status updates"""
    self.update_state(state='PROCESSING')
    print(f"Processing task: {task_data}")
    return {"status": "completed", "data": task_data}

def check_redis_queue():
    """Check Redis queue and process tasks"""
    print(f"Starting queue check on {settings.REDIS_TASKS_QUEUE}")
    while True:
        try:
            # Get task from queue (blocking pop with timeout)
            task_data = redis_client.blpop(settings.REDIS_TASKS_QUEUE, timeout=5)
            
            if task_data:
                # task_data is a tuple (queue_name, value)
                task_json = task_data[1]
                task = json.loads(task_json)
                
                # Process the task using Celery
                result = process_task.delay(task['data'])
                print(f"Enqueued task {result.id}")
        except Exception as e:
            print(f"Error processing task: {e}")

if __name__ == "__main__":
    print("Starting Celery client...")
    check_redis_queue()