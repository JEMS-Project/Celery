import pytest
from app.services.scraper import JobScraperService

def test_scrape_jobs():
    scraper = JobScraperService()
    jobs = scraper.scrape_jobs("python", "remote", 5)
    assert isinstance(jobs, list)
    if jobs:
        assert all(key in jobs[0] for key in ['title', 'company', 'location'])

def test_fetch_description():
    scraper = JobScraperService()
    description = scraper.fetch_description("https://example.com", "linkedin")
    assert description is None or isinstance(description, str)
