from typing import List, Dict
import numpy as np

class EmbeddingRepository:
    def __init__(self, index):
        self.index = index

    def upsert_embeddings(self, vectors: List[Dict]):
        if vectors:
            self.index.upsert(vectors=vectors)
            return len(vectors)
        return 0

    def search_similar(self, vector: List[float], limit: int = 10):
        return self.index.query(
            vector=vector,
            top_k=limit,
            include_metadata=True
        )
