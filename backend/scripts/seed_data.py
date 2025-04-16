from app.db.connection import SessionLocal
from app.db.models import Job

def seed_database():
    db = SessionLocal()
    try:
        sample_jobs = [
            {
                "id": "1",
                "title": "Senior Python Developer",
                "company": "TechCorp",
                "location": "Remote",
                "description": "Looking for an experienced Python developer...",
                "url": "https://example.com/job1"
            },
            {
                "id": "2",
                "title": "Frontend Engineer",
                "company": "WebTech",
                "location": "New York",
                "description": "Frontend development position...",
                "url": "https://example.com/job2"
            }
        ]
        
        for job_data in sample_jobs:
            job = Job(**job_data)
            db.merge(job)
        db.commit()
        print("Database seeded successfully!")
        
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
