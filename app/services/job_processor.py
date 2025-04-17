from typing import List, Dict
from app.db.repositories.jobs import JobRepository
from app.services.embeddings import EmbeddingService
from app.schemas.jobs import JobCreate

class JobProcessingService:
    def __init__(self, job_repository: JobRepository, embedding_service: EmbeddingService):
        self.job_repository = job_repository
        self.embedding_service = embedding_service
    
    async def process_jobs(self, raw_jobs: List[Dict], task_id: str) -> Dict:
        """Process scraped jobs: store and generate embeddings"""
        try:
            # Store raw jobs
            stored_jobs = await self.job_repository.bulk_create_raw_jobs(
                raw_jobs, task_id
            )
            
            # Process and store normalized jobs
            processed_jobs = await self.job_repository.bulk_create_processed_jobs(
                stored_jobs, task_id
            )
            
            # Generate and store embeddings
            embeddings = []
            for job in processed_jobs:
                job_id, embedding = self.embedding_service.generate_job_embedding(job)
                if self.embedding_service.is_valid_embedding(embedding):
                    embeddings.append({
                        'id': job_id,
                        'values': embedding,
                        'metadata': {
                            'title': job.title,
                            'company': job.company,
                            'location': job.location
                        }
                    })
            
            # Batch upsert embeddings
            if embeddings:
                self.embedding_service.upsert_embeddings(embeddings)
                
            return {
                'raw_jobs_stored': len(stored_jobs),
                'processed_jobs': len(processed_jobs),
                'embeddings_created': len(embeddings)
            }
            
        except Exception as e:
            print(f"Error processing jobs: {e}")
            raise
