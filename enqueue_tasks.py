import redis
import json
from datetime import datetime

# Connect to Upstash Redis
redis_client = redis.Redis(
    host='leading-maggot-35090.upstash.io',
    port=6379,
    password='AYkSAAIjcDExMTliZjEzNzE4YTc0MzYzOWU2NTkzMmYwNjhmNzRhNXAxMA',
    ssl=True,
    decode_responses=True  # Add this to get strings instead of bytes
)

def enqueue_task(task_data):
    # Create task with timestamp
    task = {
        'data': task_data,
        'timestamp': datetime.now().isoformat(),
        'status': 'pending'
    }
    
    # Convert task to JSON string
    task_json = json.dumps(task)
    
    # Push task to Redis queue
    redis_client.rpush('task_queue', task_json)
    print(f"Enqueued task: {task_data}")

if __name__ == "__main__":
    # Sample tasks
    sample_tasks = [
        {"task_id": 1, "description": "Scrap Jobs"},
        {"task_id": 2, "description": "Upload Jobs to Turso DB"},
        {"task_id": 3, "description": "Upsert Job Embeddings to Pinecone"}
    ]
    
    # Enqueue sample tasks
    for task in sample_tasks:
        enqueue_task(task)