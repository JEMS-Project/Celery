from jobspy import scrape_jobs
from typing import List, Dict
import requests
from bs4 import BeautifulSoup
from app.core.config import settings
import pandas as pd

class JobScraperService:
    def __init__(self):
        self.site_names = ["indeed", "linkedin", "glassdoor", "ziprecruiter"]

    def scrape_jobs(self, parameters: Dict) -> List[Dict]:
        """Scrape jobs based on parameters"""
        try:
            jobs = scrape_jobs(
                site_name=parameters.get('site_name', ["linkedin", "glassdoor"]),
                search_term=parameters['job_title'],
                location=parameters['location'],
                results_wanted=parameters.get('num_jobs', 20),
                country_indeed=parameters.get('country', 'USA'),
            )
            
            # Convert to list of dicts
            jobs_list = jobs.to_dict('records')
            
            # Add metadata
            for job in jobs_list:
                job['external_id'] = str(job.get('id', ''))
                job['source_site'] = job.get('site', '')
            
            return jobs_list
            
        except Exception as e:
            print(f"Error scraping jobs: {e}")
            raise

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
