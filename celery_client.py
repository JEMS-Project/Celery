'''
Keep the Worker Running
Leave this terminal open.
celery -A celery_client worker --loglevel=info --pool=solo

Run tasks by importing and calling the task directly:
from celery_client import process_task
result = process_task.delay(task_data)
'''

from celery import Celery
from app.core.config import settings
from celery.signals import worker_ready
from app.db.connection import init_connection_pool
import json
from pprint import pprint

app = Celery('celery_client')

# Set configuration
app.conf.update(
    # Broker and Backend settings
    broker_url=settings.celery_broker_url,
    result_backend=settings.celery_result_backend_url,

    # Serialization settings
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],

    # Task settings
    task_track_started=True,
    task_ignore_result=False,
    result_expires=3600,
    task_default_queue=settings.REDIS_TASKS_QUEUE,
    broker_connection_retry_on_startup=True,
)

@worker_ready.connect
def on_worker_ready(sender, **kwargs):
    print("Starting Celery worker...")
    # print("Broker URL:", settings.celery_broker_url)
    # print("Result Backend URL:", settings.celery_result_backend_url)
    try:
        init_connection_pool()
        print("✅ Database connection pool initialized")
    except Exception as e:
        print(f"❌ Failed to initialize database connection pool: {e}")
        raise

@app.task(bind=True, name='celery_client.process_task')
def process_task(self, task_data):
    """Task processing function with status updates"""
    self.update_state(state='PROCESSING')
    #explain above statement 
    #print task data in json format nicely in terminal beautify

    print("Task data received:")
    print(json.dumps(task_data, indent=4))
    # print(f"Processing task: {task_data}")
    # print("Complete task data:", task_data)
    self.update_state(state='COMPLETED')

    print("Task processing completed.")
    return {"status": "completed", "data": task_data}

if __name__ == "__main__":
    app.start()