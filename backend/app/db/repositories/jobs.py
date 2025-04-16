from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List, Dict
from app.db.models import Job
from app.schemas.jobs import JobCreate

class JobRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_job(self, job_data: Dict) -> Job:
        db_job = Job(**job_data)
        self.db.add(db_job)
        self.db.commit()
        self.db.refresh(db_job)
        return db_job

    def get_jobs_by_ids(self, job_ids: List[str]) -> List[Job]:
        return self.db.execute(
            select(Job).where(Job.id.in_(job_ids))
        ).scalars().all()

    def bulk_create_jobs(self, jobs_data: List[Dict]) -> List[Job]:
        jobs = [Job(**job_data) for job_data in jobs_data]
        self.db.bulk_save_objects(jobs)
        self.db.commit()
        return jobs
