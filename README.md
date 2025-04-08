# Celery Job Scraper

## Local Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Copy `.env.example` to `.env` and fill in credentials.
3. Start worker: `celery -A src.main.celery_app worker --loglevel=info --pool=solo`
4. Enqueue tasks: `python tests/enqueue_tasks.py`

## Docker
1. Build: `docker build -t celery-job-scraper .`
2. Run: `docker run --env-file .env celery-job-scraper`

## HF Spaces
1. Push to HF repo.
2. Set Repository Secrets for .env vars.