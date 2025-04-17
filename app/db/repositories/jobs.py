from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List, Dict
from app.db.models import Job, RawJob, ProcessedJob
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

    async def bulk_create_raw_jobs(self, jobs_data: List[Dict], task_id: str) -> List[RawJob]:
        """Store raw scraped jobs"""
        raw_jobs = [
            RawJob(
                task_id=task_id,
                external_id=job.get('external_id'),
                raw_data=job,
                source_site=job.get('source_site')
            )
            for job in jobs_data
        ]
        self.db.bulk_save_objects(raw_jobs)
        await self.db.commit()
        return raw_jobs

    async def bulk_create_processed_jobs(self, raw_jobs: List[RawJob], task_id: str) -> List[ProcessedJob]:
        """Create processed jobs from raw jobs"""
        processed_jobs = []
        for raw_job in raw_jobs:
            data = raw_job.raw_data
            processed_job = ProcessedJob(
                raw_job_id=raw_job.id,
                task_id=task_id,
                title=data.get('title'),
                company=data.get('company'),
                location=data.get('location'),
                description=data.get('description'),
                url=data.get('url'),
                salary_min=data.get('salary_min'),
                salary_max=data.get('salary_max'),
                salary_currency=data.get('salary_currency'),
                job_type=data.get('job_type')
            )
            processed_jobs.append(processed_job)
        
        self.db.bulk_save_objects(processed_jobs)
        await self.db.commit()
        return processed_jobs
