from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

class JobStatus(str, Enum):
    PENDING = "PENDING"
    RESEARCHING = "RESEARCHING"
    SCRIPTING = "SCRIPTING"
    VALIDATING = "VALIDATING"
    RENDERING = "RENDERING"
    STITCHING = "STITCHING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class GenerateLessonRequest(BaseModel):
    topic_id: str  # "PHY12_01_02"
    teacher_name: str = "Teacher"
    language: str = "English"
    tone: str = "Exam Focus"
    avatar_id: Optional[str] = None

class JobResponse(BaseModel):
    job_id: str
    status: JobStatus
    message: str = ""
    result: Optional[str] = None

class TopicItem(BaseModel):
    topic_id: str
    title: str
    is_ready: bool # True if "Core Lesson" is already cached

class ChapterItem(BaseModel):
    chapter_id: str
    title: str
    topics: List[TopicItem]

class BookStructure(BaseModel):
    book_id: str
    chapters: List[ChapterItem]

class ChatRequest(BaseModel):
    message: str
    history: List[dict] = [] # [{"role": "user", "content": "..."}]

class ChatResponse(BaseModel):
    reply: str
    sources: List[str] = []

class UploadURLRequest(BaseModel):
    filename: str
    content_type: str = "application/pdf"

class ProcessFileRequest(BaseModel):
    gcs_uri: str
