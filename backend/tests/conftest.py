import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.models import Base
from app.db.repositories.jobs import JobRepository
from app.services.embeddings import EmbeddingService

@pytest.fixture
def test_db():
    engine = create_engine('sqlite:///:memory:')
    TestingSessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def job_repository(test_db):
    return JobRepository(test_db)

@pytest.fixture
def embedding_service():
    return EmbeddingService()
