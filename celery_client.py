'''
Keep the Worker Running
Leave this terminal open.
celery -A celery_client worker --loglevel=info --pool=solo

Run tasks by importing and calling the task directly:
from celery_client import process_task
result = process_task.delay(task_data)
'''

from celery_tasks.worker import app
from celery_tasks.tasks.scraping import process_job_task

process_task = process_job_task

if __name__ == "__main__":
    app.start()