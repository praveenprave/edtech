from fastapi import FastAPI, BackgroundTasks, HTTPException
from contextlib import asynccontextmanager
from dotenv import load_dotenv

load_dotenv()
from app.models import GenerateLessonRequest, JobResponse, JobStatus
from app.services.heygen import HeyGenClient
from app.agents import ResearchAgent, ScriptwriterAgent, ValidationAgent
import uuid
import os

from app.services.db import DatabaseService
from app.services.parser import DocumentParser
from app.services.stitcher import StitcherService
from app.services.storage import StorageService
from pydantic import BaseModel

# Initialize Services
db_service = DatabaseService()
stitcher_service = StitcherService()
storage_service = StorageService() 
# Note: Parser requires DOCAI_PROCESSOR_ID env var to work effectively
doc_parser = DocumentParser(project_id=os.getenv("GOOGLE_CLOUD_PROJECT", "demo"))

jobs_db = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Textbook RAG Platform Starting...")
    yield
    print("🛑 Shutting down...")

app = FastAPI(title="Textbook-to-Video RAG Platform", lifespan=lifespan)

async def process_lesson_job(job_id: str, request: GenerateLessonRequest):
    """
    Orchestrates the Smart Content Pipeline: Core Lesson Lookup -> Personalization -> Assembly.
    """
    print(f"[{job_id}] 🏁 Starting Lesson Orchestration for Topic: {request.topic_id}")
    
    try:
        # services
        researcher = ResearchAgent()
        scriptwriter = ScriptwriterAgent()
        heygen = HeyGenClient()
        db = DatabaseService()

        # Step 1: Check Library for Core Lesson
        jobs_db[job_id]["status"] = JobStatus.RESEARCHING # checking cache
        core_video_url = db.get_core_lesson(request.topic_id)
        
        if not core_video_url:
            print(f"[{job_id}] ⚡ Cache Miss. Generating Core Lesson from RAG...")
            # 1.1 RAG lookup for Topic
            # In a real app, RAGService would query by topic metadata ("Chapter 1.2")
            fact_brief = researcher.research(f"Explain {request.topic_id}") 
            
            # 1.2 Script & Produce Core
            jobs_db[job_id]["status"] = JobStatus.SCRIPTING
            core_script = scriptwriter.generate(f"Create a 5-minute core lesson script on: {fact_brief}")
            
            # 1.3 Render Core
            jobs_db[job_id]["status"] = JobStatus.RENDERING
            # core_video_url = heygen.generate(core_script) # Simulated
            core_video_url = "https://mock.com/core_lesson_coulombs.mp4"
            
            # 1.4 Cache it
            db.cache_core_lesson(request.topic_id, core_video_url)
        else:
            print(f"[{job_id}] ✅ Library Hit! Using pre-generated Core Lesson.")

        # Step 2: Personalization (The Teacher's Layer)
        jobs_db[job_id]["status"] = "PERSONALIZING" 
        intro_prompt = f"Write a 15-second intro for {request.teacher_name}'s class. Topic: {request.topic_id}. Tone: {request.tone}. Date: Today."
        intro_script = scriptwriter.generate(intro_prompt)
        print(f"[{job_id}] 👤 Generated Custom Intro Script: {intro_script[:50]}...")
        
        # intro_video_url = heygen.generate(intro_script, avatar=request.avatar_id)
        intro_video_url = "https://mock.com/custom_intro.mp4"

        # Step 3: Stitching (Assembly)
        jobs_db[job_id]["status"] = JobStatus.STITCHING
        print(f"[{job_id}] 🧵 Stitching: [Custom Intro] + [Core Lesson]...")
        
        # Use the real Stitcher Service
        final_video_url = stitcher_service.stitch(intro_video_url, core_video_url)
        print(f"[{job_id}] ✅ Stiching Complete! Final URL: {final_video_url}")

        jobs_db[job_id]["status"] = JobStatus.COMPLETED
        jobs_db[job_id]["message"] = f"Lesson Ready! Confidence: 94%"
        jobs_db[job_id]["result"] = final_video_url

    except Exception as e:
        print(f"[{job_id}] ❌ Job Failed: {e}")
        jobs_db[job_id]["status"] = JobStatus.FAILED
        jobs_db[job_id]["message"] = str(e)

@app.get("/api/v1/book-structure")
async def get_book_structure(gcs_uri: str = "default"):
    """
    Returns the Smart Topic Tree (Chapters > Topics)
    """
    return doc_parser.extract_hierarchy(gcs_uri)

@app.post("/api/v1/generate", response_model=JobResponse)
async def generate_lesson(request: GenerateLessonRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    jobs_db[job_id] = {"job_id": job_id, "status": JobStatus.QUEUED}
    background_tasks.add_task(process_lesson_job, job_id, request)
    return JobResponse(
        job_id=job_id,
        status=JobStatus.QUEUED,
        message="Request queued. The Brain is analyzing your query."
    )

class UploadURLRequest(BaseModel):
    filename: str
    content_type: str = "application/pdf"

@app.post("/api/v1/upload-url")
async def get_upload_url(request: UploadURLRequest):
    """
    Generates a generic Presigned URL to upload a file directly to GCS.
    """
    try:
        return storage_service.generate_upload_url(request.filename, request.content_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/jobs/{job_id}", response_model=JobResponse)
async def get_job_status(job_id: str):
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs_db[job_id]
    return JobResponse(
        job_id=job_id,
        status=job["status"],
        message=job.get("message", f"Current Step: {job['status']}")
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
