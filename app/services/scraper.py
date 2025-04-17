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
            df_jobs = scrape_jobs(
                site_name=parameters.get('site_name', ["linkedin", "glassdoor"]),
                search_term=parameters['job_title'],
                location=parameters['location'],
                results_wanted=parameters.get('num_jobs', 20),
                country_indeed=parameters.get('country', 'USA'),
            )
            
            # Convert DataFrame to list of dicts and normalize the data
            jobs_list = []
            for _, row in df_jobs.iterrows():
                job = {
                    'external_id': str(row.get('id', '')),
                    'title': row.get('title', ''),
                    'company': row.get('company', ''),
                    'location': row.get('location', ''),
                    'description': row.get('description', ''),
                    'job_url': row.get('job_url', ''),
                    'job_type': row.get('job_type', ''),
                    'salary_interval': row.get('interval', ''),
                    'salary_min': row.get('min_amount'),
                    'salary_max': row.get('max_amount'),
                    'salary_currency': row.get('currency', 'USD'),
                    'source_site': row.get('site', ''),
                    'raw_data': row.to_dict()
                }
                jobs_list.append(job)
            
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
