-- Database Schema for Textbook-to-Video RAG Platform
-- Based on User Architecture
-- WARNING: This drops existing tables to ensure clean schema update during POC.
DROP TABLE IF EXISTS teacher_jobs CASCADE;
DROP TABLE IF EXISTS video_library CASCADE;
DROP TABLE IF EXISTS visual_assets CASCADE;
DROP TABLE IF EXISTS topics CASCADE;
DROP TABLE IF EXISTS chapters CASCADE;
DROP TABLE IF EXISTS books CASCADE;

-- 1. Books (The Source)
CREATE TABLE IF NOT EXISTS books (
    book_id VARCHAR(50) PRIMARY KEY, -- e.g. "TN_SCERT_PHY_12"
    title VARCHAR(255) NOT NULL,
    subject VARCHAR(50),
    board VARCHAR(50),
    grade_level INTEGER,
    language VARCHAR(20) DEFAULT 'English',
    gcs_uri VARCHAR(255) NOT NULL, -- "gs://.../textbook.pdf"
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Structure (The Parser Output)
CREATE TABLE IF NOT EXISTS chapters (
    chapter_id VARCHAR(50) PRIMARY KEY, -- "PHY12_01"
    book_id VARCHAR(50) REFERENCES books(book_id),
    chapter_number INTEGER,
    title VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS topics (
    topic_id VARCHAR(50) PRIMARY KEY, -- "PHY12_01_02"
    chapter_id VARCHAR(50) REFERENCES chapters(chapter_id),
    title VARCHAR(255) NOT NULL, -- "Electric Field Lines"
    page_start INTEGER,
    page_end INTEGER,
    content_hash VARCHAR(100) -- To detect content changes
);

-- 3. Visual Assets: Extracted diagrams and flowcharts
CREATE TABLE IF NOT EXISTS visual_assets (
    asset_id SERIAL PRIMARY KEY,
    topic_id VARCHAR(50) REFERENCES topics(topic_id),
    image_url TEXT NOT NULL,       -- GCS URL of the cropped diagram
    description TEXT,              -- AI Generated description (Vision Agent)
    original_page_number INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Video Library: The Cache for generated lessons
CREATE TABLE IF NOT EXISTS video_library (
    video_id SERIAL PRIMARY KEY,
    topic_id VARCHAR(50) REFERENCES topics(topic_id),
    video_url TEXT NOT NULL,       -- Final MP4 URL in GCS
    transcript TEXT,               -- Full transcript for validation
    confidence_score FLOAT,        -- 0.0 to 1.0 (Validator Agent Output)
    status VARCHAR(50) DEFAULT 'processed', -- 'processed', 'flagged'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. Teacher Jobs: Tracking live requests
CREATE TABLE IF NOT EXISTS teacher_jobs (
    job_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    teacher_id VARCHAR(255) NOT NULL,
    topic_query VARCHAR(255),      -- Original input e.g. "Explain Plants"
    matched_topic_id VARCHAR(50) REFERENCES topics(topic_id),
    status VARCHAR(50) DEFAULT 'queued', -- 'queued', 'researching', 'scripting', 'rendering', 'validating', 'completed', 'failed'
    current_step VARCHAR(100),     -- For detailed UI progress bars
    result_video_id INTEGER REFERENCES video_library(video_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_books_meta ON books(subject, grade_level, board);
CREATE INDEX idx_topics_title ON topics(title);
CREATE INDEX idx_jobs_teacher ON teacher_jobs(teacher_id);
