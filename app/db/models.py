from dataclasses import dataclass
from typing import Optional, Dict

@dataclass
class RawJob:
    id: int
    task_id: str
    external_id: str
    raw_data: Dict
    source_site: str
    title: str
    company: str
    location: Optional[str] = None
    job_url: Optional[str] = None
    job_type: Optional[str] = None
    salary_interval: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary_currency: Optional[str] = None
    description: Optional[str] = None

@dataclass
class ProcessedJob:
    id: int
    raw_job_id: int
    task_id: str
    title: str
    company: str
    location: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary_currency: Optional[str] = None
    job_type: Optional[str] = None
