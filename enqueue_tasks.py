from celery_client import process_task

def enqueue_sample_task():
    # Example task data
    task_data = {"job_id": 123, "action": "process"}
    
    # Send task to Celery
    result = process_task.delay(task_data)
    print(f"Enqueued task with id: {result.id}")
    return result

if __name__ == "__main__":
    result = enqueue_sample_task()
    print("Task enqueued successfully")
