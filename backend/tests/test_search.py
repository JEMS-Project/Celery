import pytest
from app.services.search import JobSearchService
from app.services.embeddings import EmbeddingService
from app.db.repositories.jobs import JobRepository

def test_search_jobs(mocker):
    mock_embedding_service = mocker.Mock(spec=EmbeddingService)
    mock_job_repository = mocker.Mock(spec=JobRepository)
    
    mock_embedding_service.generate_embedding.return_value = [0.1] * 384
    mock_embedding_service.index.query.return_value = {
        'matches': [{'id': '1'}, {'id': '2'}]
    }
    
    search_service = JobSearchService(mock_embedding_service, mock_job_repository)
    result = search_service.search_jobs("python developer")
    
    assert mock_embedding_service.generate_embedding.called
    assert mock_job_repository.get_jobs_by_ids.called
