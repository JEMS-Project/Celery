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
from dotenv import load_dotenv
import os

load_dotenv()

# Configure Celery using environment variables
app = Celery('celery_client',
             broker=os.getenv('UPSTASH_REDIS_URL'),
             backend=os.getenv('UPSTASH_REDIS_URL'),
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
    task_default_queue=os.getenv('CELERY_TASK_QUEUE', 'celery'),
)

# Redis client configuration from environment
redis_client = redis.Redis(
    host=os.getenv('UPSTASH_REDIS_HOST'),
    port=int(os.getenv('UPSTASH_REDIS_PORT', 6379)),
    password=os.getenv('UPSTASH_REDIS_PASSWORD'),
    ssl=True,
    decode_responses=True
)

@app.task(name='celery_client.process_task')
def process_task(task_data):
    """Task processing function"""
    print(f"Processing task: {task_data}")
    return f"Completed: {task_data}"

def check_redis_queue():
    """Check Redis queue and process tasks"""
    while True:
        # Get task from queue (blocking pop with timeout)
        task_data = redis_client.blpop('task_queue', timeout=5)
        
        if task_data:
            # task_data is a tuple (queue_name, value)
            task_json = task_data[1]
            task = json.loads(task_json)
            
            # Process the task using Celery
            process_task.delay(task['data'])

if __name__ == "__main__":
    print("Starting Celery client...")
    check_redis_queue()