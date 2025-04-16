from pydantic import BaseModel

class JobBase(BaseModel):
    id: str
    title: str
    company: str
    location: str
    description: str
    url: str

class JobCreate(JobBase):
    pass

class Job(JobBase):
    class Config:
        from_attributes = True
