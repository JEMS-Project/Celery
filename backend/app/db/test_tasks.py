"""Test tasks for development and testing"""

SAMPLE_TASKS = [
    {
        "type": "scrape",
        "data": {
            "job_title": "Software Engineer",
            "location": "United States",
            "max_results": 20
        }
    },
    {
        "type": "scrape",
        "data": {
            "job_title": "Data Scientist",
            "location": "Remote",
            "max_results": 20
        }
    },
    {
        "type": "upload",
        "data": {
            "file_path": "jobs_data.json",
            "batch_size": 100
        }
    },
    {
        "type": "embed",
        "data": {
            "job_ids": ["recent_jobs"],
            "model": "all-MiniLM-L6-v2"
        }
    }
]
