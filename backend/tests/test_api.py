from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_scrape_endpoint():
    response = client.post(
        "/jobs/scrape",
        json={
            "search_term": "python developer",
            "location": "remote",
            "results_wanted": 5
        }
    )
    assert response.status_code == 200
    assert "task_id" in response.json()
