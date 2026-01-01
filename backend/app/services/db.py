import os
import sqlalchemy
from sqlalchemy import create_engine, text
from typing import Optional

class DatabaseService:
    """
    Manages Caching of generated videos to avoid redundant RAG + Rendering costs.
    """
    def __init__(self):
        self.db_user = os.getenv("DB_USER", "postgres")
        self.db_pass = os.getenv("DB_PASS", "supersecretDBpassword123")
        self.db_name = os.getenv("DB_NAME", "rag_platform")
        self.db_host = os.getenv("DB_HOST", "127.0.0.1") # Cloud SQL Proxy or Private IP
        
        # Connection String
        self.db_url = f"postgresql+pg8000://{self.db_user}:{self.db_pass}@{self.db_host}/{self.db_name}"
        self.engine = None
        
        # Attempt Connection
        try:
            # Only connect if we are likely in a real env or have explicit config
            if os.getenv("CLOUD_SQL_CONNECTION_NAME") or os.getenv("DB_HOST"):
                 self.engine = create_engine(self.db_url)
        except Exception as e:
            print(f"⚠️ DB Init Warning: {e}")

        # In-Memory Fallback for Demo/Local without Docker Compose DB
        self.memory_cache = {}

    def get_core_lesson(self, topic_id: str) -> Optional[str]:
        """
        Checks if the generic 'Core Lesson' exists for this Topic ID.
        """
        print(f"💾 Checking Library for Topic: {topic_id}")
        
        # 1. Try DB
        if self.engine:
            try:
                with self.engine.connect() as conn:
                    # Looking up in video_library
                    result = conn.execute(
                        text("SELECT core_video_url FROM video_library WHERE topic_id = :tid"), 
                        {"tid": topic_id}
                    ).fetchone()
                    if result:
                        print(f"✅ Library Hit: {topic_id}")
                        return result[0]
            except Exception as e:
                print(f"❌ DB Read Error: {e}")

        # 2. Mock Fallback (Pretend we have cache for 1.2)
        if topic_id == "PHY12_01_02":
             return "https://mock-storage.google.com/core_lessons/coulombs_law.mp4"
        
        return None

    def cache_core_lesson(self, topic_id: str, video_url: str):
        """
        Saves the new Core Lesson to the library.
        """
        print(f"💾 Saving to Library: {topic_id}")
        
        if self.engine:
            try:
                with self.engine.connect() as conn:
                    conn.execute(
                        text("INSERT INTO video_library (topic_id, core_video_url, confidence_score) VALUES (:tid, :url, 95)"),
                        {"tid": topic_id, "url": video_url}
                    )
                    conn.commit()
            except Exception as e:
                print(f"❌ DB Write Error: {e}")
