from typing import List, Dict
from app.services.embeddings import EmbeddingService
from app.db.repositories.jobs import JobRepository

class JobSearchService:
    def __init__(self, embedding_service: EmbeddingService, job_repository: JobRepository):
        self.embedding_service = embedding_service
        self.job_repository = job_repository

    def search_jobs(self, query: str, limit: int = 10) -> List[Dict]:
        query_embedding = self.embedding_service.generate_embedding(query)
        results = self.embedding_service.index.query(
            vector=query_embedding,
            top_k=limit,
            include_metadata=True
        )
        return [match['metadata'] for match in results['matches']]
