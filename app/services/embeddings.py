import os
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Tuple
import numpy as np
from app.core.config import settings

class EmbeddingService:
    def __init__(self):
        self.pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        self.index_name = os.getenv("PINECONE_INDEX_NAME", "job-embeddings")
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

    def generate_job_embedding(self, job: Dict) -> Tuple[str, List[float]]:
        embedding_text = f"{job.get('title', '')} {job.get('company', '')} {job.get('description', '')}"
        embedding = self.model.encode(embedding_text).tolist()
        return job['id'], embedding

    def is_valid_embedding(self, embedding: List[float]) -> bool:
        return all(np.isfinite(x) for x in embedding)

    def upsert_embeddings(self, vectors):
        if vectors:
            self.index.upsert(vectors=vectors)
