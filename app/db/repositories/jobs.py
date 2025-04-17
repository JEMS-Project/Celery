from typing import List, Dict
import json
from app.db.models import Job, RawJob, ProcessedJob

class JobRepository:
    def __init__(self, db_conn):
        self.conn = db_conn

    async def create_job(self, job_data: Dict) -> Job:
        """Create a basic job entry"""
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO processed_jobs (title, company, location, description, url)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """, (
                job_data['title'],
                job_data['company'],
                job_data.get('location'),
                job_data.get('description'),
                job_data.get('url')
            ))
            job_id = cursor.fetchone()[0]
            self.conn.commit()
            return Job(id=job_id, **job_data)
        finally:
            cursor.close()

    def get_jobs_by_ids(self, job_ids: List[str]) -> List[Dict]:
        """Get jobs by their IDs using raw SQL"""
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                SELECT id, title, company, location, description, url 
                FROM processed_jobs 
                WHERE id = ANY(%s)
            """, (job_ids,))
            
            jobs = cursor.fetchall()
            return [
                {
                    'id': job[0],
                    'title': job[1],
                    'company': job[2],
                    'location': job[3],
                    'description': job[4],
                    'url': job[5]
                }
                for job in jobs
            ]
        finally:
            cursor.close()

    def bulk_create_jobs(self, jobs_data: List[Dict]) -> List[Job]:
        jobs = [Job(**job_data) for job_data in jobs_data]
        self.db.bulk_save_objects(jobs)
        self.db.commit()
        return jobs

    async def bulk_create_raw_jobs(self, jobs_data: List[Dict], task_id: str) -> List[RawJob]:
        cursor = self.conn.cursor()
        raw_jobs = []
        
        try:
            # Prepare values for bulk insert
            values = [(
                task_id,
                job.get('external_id'),
                json.dumps(job),
                job.get('source_site')
            ) for job in jobs_data]
            
            # Bulk insert using executemany
            cursor.executemany("""
                INSERT INTO raw_jobs (task_id, external_id, raw_data, source_site)
                VALUES (%s, %s, %s, %s)
                RETURNING id
            """, values)
            
            # Get the inserted IDs
            inserted_ids = cursor.fetchall()
            
            # Create RawJob objects
            for (id,), job_data in zip(inserted_ids, jobs_data):
                raw_jobs.append(RawJob(
                    id=id,
                    task_id=task_id,
                    external_id=job_data.get('external_id'),
                    raw_data=job_data,
                    source_site=job_data.get('source_site')
                ))
            
            self.conn.commit()
            return raw_jobs
            
        except Exception as e:
            self.conn.rollback()
            raise e
        finally:
            cursor.close()

    async def bulk_create_processed_jobs(self, raw_jobs: List[RawJob], task_id: str) -> List[ProcessedJob]:
        cursor = self.conn.cursor()
        processed_jobs = []
        
        try:
            values = []
            for raw_job in raw_jobs:
                data = raw_job.raw_data
                values.append((
                    raw_job.id,
                    task_id,
                    data.get('title'),
                    data.get('company'),
                    data.get('location'),
                    data.get('description'),
                    data.get('url'),
                    data.get('salary_min'),
                    data.get('salary_max'),
                    data.get('salary_currency'),
                    data.get('job_type')
                ))
            
            cursor.executemany("""
                INSERT INTO processed_jobs (
                    raw_job_id, task_id, title, company, location, 
                    description, url, salary_min, salary_max, 
                    salary_currency, job_type
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, values)
            
            inserted_ids = cursor.fetchall()
            
            for (id,), (raw_job, value) in zip(inserted_ids, zip(raw_jobs, values)):
                processed_jobs.append(ProcessedJob(
                    id=id,
                    raw_job_id=value[0],
                    task_id=value[1],
                    title=value[2],
                    company=value[3],
                    location=value[4],
                    description=value[5],
                    url=value[6],
                    salary_min=value[7],
                    salary_max=value[8],
                    salary_currency=value[9],
                    job_type=value[10]
                ))
            
            self.conn.commit()
            return processed_jobs
            
        except Exception as e:
            self.conn.rollback()
            raise e
        finally:
            cursor.close()
