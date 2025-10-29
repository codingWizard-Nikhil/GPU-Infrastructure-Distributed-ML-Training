from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from database import get_db, JobModel
from pydantic import BaseModel

class JobSubmit(BaseModel):
    code: str

class JobResponse(BaseModel):
    id: str
    status: str
    code: str
    submitted_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None
    result: str | None = None
    error: str | None = None

    class Config:
        from_attributes = True

app = FastAPI(title="Remote Compute Server")

@app.get("/")
def home():
    return {"message": "Server is running!"}

@app.get("/health")
def health():
    return {"status" : "healthy"}

@app.post("/jobs", response_model=JobResponse)
def create_job(job: JobSubmit, db: Session = Depends(get_db)):
    """Submit a new job"""
    new_job = JobModel(
        code=job.code,
        status="pending",
        submitted_at=datetime.now(timezone.utc)
    )
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    return new_job

@app.get("/jobs/{job_id}", response_model=JobResponse)
def get_job(job_id: str, db: Session = Depends(get_db)):
    """Get job by ID"""
    job = db.query(JobModel).filter(JobModel.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@app.get("/jobs", response_model=list[JobResponse])
def list_jobs(db: Session = Depends(get_db)):
    """List all jobs"""
    jobs = db.query(JobModel).order_by(JobModel.submitted_at.desc()).all()
    return jobs