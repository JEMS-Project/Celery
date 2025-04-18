from celery_tasks.worker import app
from app.services.scraper import JobScraperService
from app.services.job_processor import JobProcessingService
from app.db.repositories.jobs import JobRepository
from app.services.embeddings import EmbeddingService
from app.db.connection import get_db_connection
from asgiref.sync import async_to_sync
from datetime import datetime
import json

@app.task(bind=True, name='tasks.process_job_task')
def process_job_task(self, task_data):
    """Process complete job scraping and embedding workflow"""
    task_id = task_data['request_id']
    self.update_state(state='PROCESSING')
    
    try:
        # Initialize services and scrape jobs
        scraper = JobScraperService()
        raw_jobs = scraper.scrape_jobs(task_data['parameters'])
        
        # Process jobs with DB connection
        with get_db_connection() as db:
            cursor = db.cursor()
            try:
                # First create the task record - serialize task_data to JSON
                cursor.execute("""
                    INSERT INTO celery_tasks (
                        task_id, 
                        status, 
                        task_name, 
                        task_args,
                        created_at
                    ) VALUES (%s, %s, %s, %s, %s)
                """, (
                    task_id,
                    'PROCESSING',
                    'scrape_jobs',
                    json.dumps(task_data),  # Convert dict to JSON string
                    datetime.utcnow()
                ))
                db.commit()

                # Now process the jobs
                job_repository = JobRepository(db)
                embedding_service = EmbeddingService()
                processor = JobProcessingService(job_repository, embedding_service)
                
                # Convert async to sync
                process_jobs_sync = async_to_sync(processor.process_jobs)
                result = process_jobs_sync(raw_jobs, task_id)

                # Update task status on success
                cursor.execute("""
                    UPDATE celery_tasks 
                    SET status = %s, 
                        completed_at = %s
                    WHERE task_id = %s
                """, ('SUCCESS', datetime.utcnow(), task_id))
                db.commit()
                
                return {
                    "status": "completed",
                    "task_id": task_id,
                    "stats": result
                }

            except Exception as e:
                # Update task status on failure
                cursor.execute("""
                    UPDATE celery_tasks 
                    SET status = %s, 
                        error_message = %s,
                        completed_at = %s
                    WHERE task_id = %s
                """, ('FAILED', str(e), datetime.utcnow(), task_id))
                db.commit()
                raise
            finally:
                cursor.close()
        
    except Exception as e:
        self.update_state(state='FAILED')
        return {
            "status": "failed",
            "task_id": task_id,
            "error": str(e)
        }
