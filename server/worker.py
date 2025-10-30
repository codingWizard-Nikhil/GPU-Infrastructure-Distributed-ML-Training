import time
import subprocess
import sys
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from database import SessionLocal, JobModel

def get_pending_job(db: Session):
    """Get the first pending job from the database."""
    job = db.query(JobModel).filter(JobModel.status == "pending").first()
    return job

def execute_job(job: JobModel, db: Session):
    """Execute a job and update its status."""
    print(f"Executing job {job.id}...")
    
    # Update status to running
    job.status = "running"
    job.started_at = datetime.now(timezone.utc)
    db.commit()
    
    try:
        # Execute the Python code
        result = subprocess.run(
            [sys.executable, "-c", job.code],
            capture_output=True,
            text=True,
            timeout=60  # 60 second timeout
        )
        
        # Store results
        job.result = result.stdout
        job.error = result.stderr if result.returncode != 0 else None
        job.status = "completed" if result.returncode == 0 else "failed"
        job.completed_at = datetime.now(timezone.utc)
        
        print(f"Job {job.id} completed with status: {job.status}")
        
    except subprocess.TimeoutExpired:
        job.status = "failed"
        job.error = "Job execution timed out (60 seconds)"
        job.completed_at = datetime.now(timezone.utc)
        print(f"Job {job.id} timed out")
        
    except Exception as e:
        job.status = "failed"
        job.error = str(e)
        job.completed_at = datetime.now(timezone.utc)
        print(f"Job {job.id} failed with error: {e}")
    
    finally:
        db.commit()

def main():
    """Main worker loop."""
    print("Worker started. Polling for jobs...")
    
    while True:
        db = SessionLocal()
        try:
            job = get_pending_job(db)
            if job:
                execute_job(job, db)
            else:
                # No pending jobs, wait before checking again
                time.sleep(30)
        finally:
            db.close()

if __name__ == "__main__":
    main()