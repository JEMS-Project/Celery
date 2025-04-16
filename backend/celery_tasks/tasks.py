from .worker import app
from app.services.scraper import JobScraperService
from app.services.embeddings import EmbeddingService
from app.db.repositories.jobs import JobRepository
from app.db.connection import SessionLocal

@app.task(name='tasks.scrape_and_process_jobs')
def scrape_and_process_jobs(search_term: str, location: str, results_wanted: int):
    scraper = JobScraperService()
    embedding_service = EmbeddingService()
    
    with SessionLocal() as db:
        job_repository = JobRepository(db)
        
        try:
            # Scrape jobs
            jobs = scraper.scrape_jobs(search_term, location, results_wanted)
            
            # Store jobs
            stored_jobs = job_repository.bulk_create_jobs(jobs)
            
            # Generate and store embeddings
            for job in stored_jobs:
                job_id, embedding = embedding_service.generate_job_embedding(job.__dict__)
                if embedding_service.is_valid_embedding(embedding):
                    # Store embedding in Pinecone
                    # ... implement pinecone storage ...
                    pass
            
            return {
                "status": "success",
                "jobs_processed": len(stored_jobs)
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
