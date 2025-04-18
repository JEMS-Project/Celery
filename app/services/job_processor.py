from typing import List, Dict
from app.db.repositories.jobs import JobRepository
from app.services.embeddings import EmbeddingService
from app.schemas.jobs import JobCreate
from app.core.logging import JobLogger, log_operation

class JobProcessingService:
    def __init__(self, job_repository: JobRepository, embedding_service: EmbeddingService):
        self.logger = JobLogger("JobProcessor")
        self.job_repository = job_repository
        self.embedding_service = embedding_service

    def _clean_metadata(self, metadata: Dict) -> Dict:
        """Clean metadata to ensure valid values for Pinecone"""
        return {
            k: str(v) if v is not None else ""
            for k, v in metadata.items()
        }
    
    @log_operation(JobLogger("JobProcessor"))
    async def process_jobs(self, raw_jobs: List[Dict], task_id: str) -> Dict:
        """Process scraped jobs: store and generate embeddings"""
        try:
            self.logger.log_operation(
                "Starting job processing",
                {"task_id": task_id, "job_count": len(raw_jobs)}
            )
            
            # Log each step with detailed information
            stored_jobs = await self.job_repository.bulk_create_raw_jobs(
                raw_jobs, task_id
            )
            self.logger.log_operation(
                "Raw jobs stored",
                {"count": len(stored_jobs)}
            )
            
            processed_jobs = await self.job_repository.bulk_create_processed_jobs(
                stored_jobs, task_id
            )
            self.logger.log_operation(
                "Jobs processed",
                {"count": len(processed_jobs)}
            )
            
            embeddings = []
            successful_embeddings = 0
            failed_embeddings = 0

            for job in processed_jobs:
                try:
                    # Log before generating embedding
                    self.logger.log_operation(
                        "Processing job for embedding",
                        {
                            "job_id": job.id,
                            "title": job.title,
                            "company": job.company
                        }
                    )
                    
                    job_id, embedding = self.embedding_service.generate_job_embedding(job)
                    if self.embedding_service.is_valid_embedding(embedding):
                        # Clean metadata before adding to embeddings
                        metadata = self._clean_metadata({
                            'title': job.title,
                            'company': job.company,
                            'location': job.location or "",
                            'job_type': job.job_type or "",
                            'url': job.url or ""
                        })
                        
                        embeddings.append({
                            'id': str(job_id),  # Ensure id is string
                            'values': embedding,
                            'metadata': metadata
                        })
                        successful_embeddings += 1
                    else:
                        failed_embeddings += 1
                        self.logger.log_operation(
                            "Invalid embedding detected",
                            {"job_id": job.id}
                        )
                except Exception as e:
                    failed_embeddings += 1
                    self.logger.log_error(e, {
                        "job_id": job.id,
                        "operation": "embedding_generation"
                    })
                    continue
            
            # Try to store embeddings if any were generated
            if embeddings:
                try:
                    self.embedding_service.upsert_embeddings(embeddings)
                except Exception as e:
                    self.logger.log_error(e, {
                        "operation": "embedding_storage",
                        "count": len(embeddings)
                    })
            
            return {
                'raw_jobs_stored': len(stored_jobs),
                'processed_jobs': len(processed_jobs),
                'embeddings_created': successful_embeddings,
                'embeddings_failed': failed_embeddings
            }
            
        except Exception as e:
            self.logger.log_error(e, {
                "task_id": task_id,
                "stage": "job_processing"
            })
            raise
