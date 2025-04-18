from jobspy import scrape_jobs
from typing import List, Dict
import requests
from bs4 import BeautifulSoup
from app.core.config import settings
import pandas as pd
import numpy as np
from app.core.logging import JobLogger, log_operation

class JobScraperService:
    def __init__(self):
        self.logger = JobLogger("JobScraper")
        self.site_names = ["indeed", "linkedin", "glassdoor", "ziprecruiter"]

    def clean_value(self, value):
        """Clean values before JSON serialization"""
        if pd.isna(value) or value is None or (isinstance(value, float) and np.isnan(value)):
            return None
        if isinstance(value, pd.Timestamp):
            return value.isoformat()
        return value

    @log_operation(JobLogger("JobScraper"))
    def scrape_jobs(self, parameters: Dict) -> List[Dict]:
        """Scrape jobs based on parameters"""
        try:
            self.logger.log_operation(
                "Scraping jobs",
                {"parameters": parameters}
            )
            
            df_jobs = scrape_jobs(
                site_name=parameters.get('site_name', ["linkedin", "glassdoor"]),
                search_term=parameters['job_title'],
                location=parameters['location'],
                results_wanted=parameters.get('num_jobs', 20),
                country_indeed=parameters.get('country', 'USA'),
            )
            
            self.logger.log_operation(
                "Raw jobs fetched",
                {"row_count": len(df_jobs)}
            )
            
            jobs_list = []
            for idx, row in df_jobs.iterrows():
                try:
                    cleaned_data = {k: self.clean_value(v) for k, v in row.to_dict().items()}
                    self.logger.log_operation(
                        f"Cleaning job data {idx}",
                        {"original": row.to_dict(), "cleaned": cleaned_data}
                    )
                    job = {
                        'external_id': str(cleaned_data.get('id', '')),
                        'title': cleaned_data.get('title', ''),
                        'company': cleaned_data.get('company', ''),
                        'location': cleaned_data.get('location', ''),
                        'description': cleaned_data.get('description', ''),
                        'job_url': cleaned_data.get('job_url', ''),
                        'job_type': cleaned_data.get('job_type'),
                        'salary_interval': cleaned_data.get('interval'),
                        'salary_min': cleaned_data.get('min_amount'),
                        'salary_max': cleaned_data.get('max_amount'),
                        'salary_currency': cleaned_data.get('currency', 'USD'),
                        'source_site': cleaned_data.get('site', ''),
                        'date_posted': cleaned_data.get('date_posted'),
                        'raw_data': cleaned_data  # Store cleaned raw data
                    }
                    jobs_list.append(job)
                except Exception as e:
                    self.logger.log_error(e, {
                        "row_index": idx,
                        "raw_data": row.to_dict()
                    })
                    continue
            
            return jobs_list
            
        except Exception as e:
            self.logger.log_error(e, {"parameters": parameters})
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
