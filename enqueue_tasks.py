from celery_client import process_task
from uuid import uuid4
# Format for task data
{
  "request_id": "a_unique_uuid_generated_by_producer",
  "task_type": "SCRAPE_AND_EMBED_JOB",
  "parameters": {
    "job_title": "Senior Backend Engineer",
    "location": "Remote",
    "country": "us",
    "num_jobs": 25,
    "site_name": ["linkedin", "glassdoor"]
  },
  "metadata": {
    "user_id": "user_abc_123",
    "request_timestamp": "2023-10-27T10:30:00Z"
  }
}

def enqueue_sample_task():
    # Example task data
    task_data = {
				"request_id": str(uuid4()),
				"task_type": "SCRAPE_AND_EMBED_JOB",
				"parameters": {
						"job_title": "Senior Backend Engineer",
						"location": "Remote",
						"country": "us",
						"num_jobs": 25,
						"site_name": ["linkedin", "glassdoor"]
				},
				"metadata": {
						"user_id": "user_abc_123",
						"request_timestamp": "2023-10-27T10:30:00Z"
				}
		}
    
    # Send task to Celery
    result = process_task.delay(task_data)
    print(f"Enqueued task with id: {result.id}")
    return result

if __name__ == "__main__":
    result = enqueue_sample_task()
    print("Task enqueued successfully")
