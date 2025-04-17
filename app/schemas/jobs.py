from pydantic import BaseModel
from typing import Optional

class JobBase(BaseModel):
    id: str
    title: str
    company: str
    location: Optional[str] = None
    description: Optional[str] = None
    job_url: str
    salary_interval: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary_currency: Optional[str] = None
    job_type: Optional[str] = None

class JobCreate(JobBase):
    pass

class Job(JobBase):
    class Config:
        from_attributes = True
