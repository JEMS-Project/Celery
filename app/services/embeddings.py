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

    def _validate_vector(self, vector: Dict) -> bool:
        """Validate vector data before upserting"""
        try:
            # Check required fields
            if not all(k in vector for k in ['id', 'values', 'metadata']):
                return False
            
            # Validate id is string
            if not isinstance(vector['id'], str):
                return False
            
            # Validate values is list of floats
            if not isinstance(vector['values'], list) or not all(isinstance(x, float) for x in vector['values']):
                return False
            
            # Validate metadata values are strings
            if not all(isinstance(v, str) for v in vector['metadata'].values()):
                return False
                
            return True
        except Exception:
            return False

    @log_operation(JobLogger("EmbeddingService"))
    def upsert_embeddings(self, vectors: List[Dict]) -> None:
        """Upsert vectors to Pinecone with validation"""
        if not vectors:
            return

        try:
            # Filter out invalid vectors
            valid_vectors = [v for v in vectors if self._validate_vector(v)]
            
            if not valid_vectors:
                self.logger.log_operation(
                    "No valid vectors to upsert",
                    {"total": len(vectors), "valid": 0}
                )
                return
                
            self.logger.log_operation(
                "Upserting vectors",
                {"total": len(vectors), "valid": len(valid_vectors)}
            )
            
            # Batch upserts in chunks of 100
            batch_size = 100
            for i in range(0, len(valid_vectors), batch_size):
                batch = valid_vectors[i:i + batch_size]
                self.index.upsert(vectors=batch)
                
        except Exception as e:
            self.logger.log_error(e, {
                "operation": "upsert_embeddings",
                "vector_count": len(vectors)
            })
            raise
