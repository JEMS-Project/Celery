from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.db.connection import get_db
from app.services.scraper import JobScraperService
from app.services.embeddings import EmbeddingService
from app.schemas.requests import ScrapeRequest
from app.db.repositories.jobs import JobRepository
from celery_tasks.worker import scrape_and_process_jobs

app = FastAPI()

@app.post("/jobs/scrape")
async def scrape_jobs(
    request: ScrapeRequest,
    db: Session = Depends(get_db)
):
    task = scrape_and_process_jobs.delay(
        request.search_term,
        request.location,
        request.results_wanted
    )
    return {"task_id": task.id}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
