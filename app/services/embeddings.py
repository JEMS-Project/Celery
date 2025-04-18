import os
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Tuple, Union
import numpy as np
from app.core.config import settings
from app.db.models import ProcessedJob
from app.core.logging import JobLogger, log_operation

class EmbeddingService:
    def __init__(self):
        self.logger = JobLogger("EmbeddingService")
        self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        self.index_name = settings.PINECONE_INDEX_NAME
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL)
        self._init_index()

    def _init_index(self):
        if self.index_name not in self.pc.list_indexes().names():
            self.pc.create_index(
                name=self.index_name,
                dimension=384,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1")
            )
        self.index = self.pc.Index(self.index_name)

    @log_operation(JobLogger("EmbeddingService"))
    def generate_job_embedding(self, job: Union[Dict, ProcessedJob]) -> Tuple[str, List[float]]:
        """Generate embedding for a job, handling both dict and ProcessedJob types"""
        try:
            # Handle both dictionary and ProcessedJob objects
            if isinstance(job, dict):
                job_id = str(job['id'])
                title = job.get('title', '')
                company = job.get('company', '')
                description = job.get('description', '')
            else:
                job_id = str(job.id)
                title = job.title or ''
                company = job.company or ''
                description = job.description or ''

            # Log the text being embedded for debugging
            self.logger.log_operation(
                "Generating embedding",
                {
                    "job_id": job_id,
                    "text_length": len(f"{title} {company} {description}")
                }
            )

            embedding = self.model.encode(f"{title} {company} {description}").tolist()
            
            # Log successful embedding generation
            self.logger.log_operation(
                "Generated embedding",
                {
                    "job_id": job_id,
                    "embedding_size": len(embedding)
                }
            )
            
            return job_id, embedding
        except Exception as e:
            self.logger.log_error(e, {
                "job_id": str(getattr(job, 'id', 'unknown')),
                "stage": "embedding_generation"
            })
            raise

    def is_valid_embedding(self, embedding: List[float]) -> bool:
        return all(np.isfinite(x) for x in embedding)

    def upsert_embeddings(self, vectors):
        if vectors:
            self.index.upsert(vectors=vectors)
