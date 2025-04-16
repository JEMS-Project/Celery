import redis
import json
from datetime import datetime
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from app.core.config import settings
from app.db.test_tasks import SAMPLE_TASKS

# Connect to Upstash Redis using config
redis_client = redis.Redis(**settings.redis_config)

def enqueue_task(task_type, task_data):
    """Enqueue a task with specified type and data"""
    task = {
        'type': task_type,
        'data': task_data,
        'timestamp': datetime.now().isoformat(),
        'status': 'pending'
    }
    task_json = json.dumps(task)
    redis_client.rpush(settings.REDIS_TASKS_QUEUE, task_json)
    print(f"Enqueued {task_type} task: {task_data}")

def list_tasks():
    """List all pending tasks in the queue"""
    tasks = redis_client.lrange(settings.REDIS_TASKS_QUEUE, 0, -1)
    if not tasks:
        print("No pending tasks in queue")
        return
    
    print("\nPending Tasks:")
    for task in tasks:
        task_data = json.loads(task)
        print(f"Type: {task_data['type']}")
        print(f"Data: {task_data['data']}")
        print(f"Timestamp: {task_data['timestamp']}")
        print(f"Status: {task_data['status']}\n")

if __name__ == "__main__":
    try:
        # Test Redis connection
        redis_client.ping()
        
        # Enqueue all sample tasks
        for task in SAMPLE_TASKS:
            enqueue_task(task["type"], task["data"])
            
        # List all enqueued tasks
        list_tasks()
            
    except redis.ConnectionError:
        print("Error: Could not connect to Redis. Check your configuration.")
        sys.exit(1)