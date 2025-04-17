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

@app.task(bind=True, name='celery_client.process_task')
def process_task(self, task_data):
    """Task processing function with status updates"""
    self.update_state(state='PROCESSING')
    print(f"Processing task: {task_data}")
    return {"status": "completed", "data": task_data}

if __name__ == "__main__":
    print(settings.celery_result_backend_url)
    app.start()