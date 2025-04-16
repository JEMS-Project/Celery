from jobspy import scrape_jobs
from typing import List, Dict
import requests
from bs4 import BeautifulSoup
from app.core.config import settings

class JobScraperService:
    def __init__(self):
        self.site_names = ["indeed", "linkedin", "glassdoor", "ziprecruiter"]

    def scrape_jobs(self, search_term: str, location: str, results_wanted: int) -> List[Dict]:
        all_jobs = []
        for site in self.site_names:
            try:
                jobs = scrape_jobs(
                    site_name=[site],
                    search_term=search_term,
                    location=location,
                    results_wanted=min(results_wanted, settings.MAX_JOBS_PER_SITE),
                    country_indeed="India" if site == "indeed" else None,
                )
                all_jobs.extend(jobs.to_dict('records'))
            except Exception as e:
                print(f"Failed to scrape {site}: {str(e)}")
        return all_jobs

    def fetch_description(self, url: str, site: str) -> str:
        try:
            response = requests.get(
                url, 
                headers={"User-Agent": settings.USER_AGENT}, 
                timeout=settings.SCRAPING_TIMEOUT
            )
            soup = BeautifulSoup(response.text, 'html.parser')
            
            selector_map = {
                "linkedin": ('div', 'description__text'),
                "glassdoor": ('div', 'desc'),
                "ziprecruiter": ('div', 'job_description'),
                "indeed": ('div', {'id': 'jobDescriptionText'})
            }
            
            if site in selector_map:
                tag, class_or_id = selector_map[site]
                desc = soup.find(tag, class_or_id if isinstance(class_or_id, str) else class_or_id)
                return desc.get_text(strip=True) if desc else None
                
            return None
        except Exception as e:
            return "Failed to fetch description"
