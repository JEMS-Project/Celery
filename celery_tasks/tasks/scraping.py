from celery_tasks.worker import app
from app.services.scraper import JobScraperService
from app.services.job_processor import JobProcessingService
from app.db.repositories.jobs import JobRepository
from app.services.embeddings import EmbeddingService
from app.db.connection import get_db_connection
from asgiref.sync import async_to_sync

@app.task(bind=True, name='tasks.process_job_task')
def process_job_task(self, task_data):
    """Process complete job scraping and embedding workflow"""
    self.update_state(state='PROCESSING')
    
    try:
        # Initialize services and scrape jobs
        scraper = JobScraperService()
        raw_jobs = scraper.scrape_jobs(task_data['parameters'])
        
        # Process jobs with DB connection
        with get_db_connection() as db:
            job_repository = JobRepository(db)
            embedding_service = EmbeddingService()
            processor = JobProcessingService(job_repository, embedding_service)
            
            # Convert async to sync
            process_jobs_sync = async_to_sync(processor.process_jobs)
            result = process_jobs_sync(raw_jobs, task_data['request_id'])
        
        self.update_state(state='COMPLETED')
        return {
            "status": "completed",
            "task_id": task_data['request_id'],
            "stats": result
        }
        
    except Exception as e:
        self.update_state(state='FAILED')
        return {
            "status": "failed",
            "task_id": task_data['request_id'],
            "error": str(e)
        }
