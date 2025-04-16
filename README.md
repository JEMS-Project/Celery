# Job Search Backend

A FastAPI and Celery-based job search backend with embedding-based semantic search.

## Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Copy `.env.example` to `.env` and fill in credentials
3. Initialize database: `python scripts/init_db.py`
4. Start Celery worker: `celery -A celery_tasks.worker worker --loglevel=info`
5. Run API server: `uvicorn main:app --reload`

## Testing
Run tests with: `pytest tests/`

## Architecture
- FastAPI for REST API
- Celery for async job processing
- SQLAlchemy + Turso for storage
- Pinecone for vector search
- Redis for task queue
