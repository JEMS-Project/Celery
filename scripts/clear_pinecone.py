import os
import sys
from pinecone import Pinecone
import time
from pathlib import Path

# Add project root to Python path
project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)

from app.core.config import settings

def clear_pinecone_index():
    """Clear all vectors from the specified Pinecone index"""
    try:
        if not settings.PINECONE_API_KEY or not settings.PINECONE_ENVIRONMENT:
            raise ValueError("Missing required Pinecone configuration")

        # Initialize Pinecone client
        pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        
        # Get the index
        index = pc.Index(settings.PINECONE_INDEX_NAME)
        
        # Get total vector count
        stats = index.describe_index_stats()
        total_vectors = stats['total_vector_count']
        
        if total_vectors == 0:
            print("Index is already empty")
            return
        
        print(f"Found {total_vectors} vectors in the index")
        confirmation = input(f"Are you sure you want to delete all {total_vectors} vectors? (yes/no): ")
        
        if confirmation.lower() != 'yes':
            print("Operation cancelled")
            return
        
        print("Deleting all vectors...")
        # Delete all vectors
        index.delete(delete_all=True, namespace='')
        
        # Wait a bit and verify deletion
        time.sleep(2)
        after_stats = index.describe_index_stats()
        if after_stats['total_vector_count'] == 0:
            print("✅ Successfully deleted all vectors")
        else:
            print(f"⚠️ Warning: {after_stats['total_vector_count']} vectors still remain")
            
    except Exception as e:
        print(f"❌ Error clearing Pinecone index: {str(e)}")
        raise

if __name__ == "__main__":
    clear_pinecone_index()