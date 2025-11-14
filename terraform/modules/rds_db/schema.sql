-- Database Schema for Diagram Maker
-- Purpose: Store user diagram drafts with metadata and version tracking
-- Tables: users, diagrams
-- Features: UUID primary keys, foreign keys, indexes, JSONB for metadata

-- Enable UUID extension for generating UUIDs
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users Table
-- Stores minimal user information (no authentication, just tracking)
CREATE TABLE IF NOT EXISTS users (
    user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Optional metadata (can be extended later)
    user_metadata JSONB DEFAULT '{}'::JSONB,

    -- Index for efficient queries
    CONSTRAINT users_user_id_key UNIQUE (user_id)
);

-- Index on created_at for sorting users by registration time
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users (created_at DESC);

-- Diagrams Table
-- Stores all diagram drafts with full metadata
CREATE TABLE IF NOT EXISTS diagrams (
    diagram_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,

    -- S3 Storage Path
    s3_path TEXT NOT NULL,

    -- Diagram Metadata
    title VARCHAR(255) NOT NULL,
    description TEXT,

    -- Original User Query
    user_query TEXT NOT NULL,

    -- Generated Mermaid Code (stored for fast access without S3 reads)
    mermaid_code TEXT NOT NULL,

    -- Status: draft, published, archived
    status VARCHAR(50) DEFAULT 'draft' CHECK (status IN ('draft', 'published', 'archived')),

    -- Version Tracking
    version INTEGER DEFAULT 1,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Foreign Key to Users
    CONSTRAINT fk_diagrams_user FOREIGN KEY (user_id)
        REFERENCES users (user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- Indexes for Performance
-- Index on user_id for fast queries by user (most common operation)
CREATE INDEX IF NOT EXISTS idx_diagrams_user_id ON diagrams (user_id);

-- Index on user_id + created_at for sorting user's diagrams by creation time
CREATE INDEX IF NOT EXISTS idx_diagrams_user_created ON diagrams (user_id, created_at DESC);

-- Index on user_id + status for filtering by status
CREATE INDEX IF NOT EXISTS idx_diagrams_user_status ON diagrams (user_id, status);

-- Index on user_id + updated_at for sorting by last update
CREATE INDEX IF NOT EXISTS idx_diagrams_user_updated ON diagrams (user_id, updated_at DESC);

-- Full-text search index on title and description (for search functionality)
CREATE INDEX IF NOT EXISTS idx_diagrams_title_search ON diagrams USING gin (to_tsvector('english', title || ' ' || COALESCE(description, '')));

-- Trigger to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_diagrams_updated_at
    BEFORE UPDATE ON diagrams
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Comments for Documentation
COMMENT ON TABLE users IS 'Stores anonymous user information for tracking diagram ownership';
COMMENT ON TABLE diagrams IS 'Stores diagram drafts with metadata, S3 paths, and mermaid code';

COMMENT ON COLUMN users.user_id IS 'Unique identifier for each user (UUID v4)';
COMMENT ON COLUMN users.user_metadata IS 'Optional JSON metadata for future extensibility';

COMMENT ON COLUMN diagrams.diagram_id IS 'Unique identifier for each diagram (UUID v4)';
COMMENT ON COLUMN diagrams.user_id IS 'Foreign key to users table';
COMMENT ON COLUMN diagrams.s3_path IS 'Full S3 path to the stored .mmd file (e.g., s3://bucket/users/{user_id}/diagrams/{diagram_id}.mmd)';
COMMENT ON COLUMN diagrams.title IS 'Human-readable title for the diagram';
COMMENT ON COLUMN diagrams.description IS 'Optional description of the diagram';
COMMENT ON COLUMN diagrams.user_query IS 'Original user query that generated this diagram';
COMMENT ON COLUMN diagrams.mermaid_code IS 'Generated mermaid flowchart code (stored in DB for fast access)';
COMMENT ON COLUMN diagrams.status IS 'Current status: draft (editable), published (shared), archived (deleted)';
COMMENT ON COLUMN diagrams.version IS 'Version number for tracking diagram updates';

-- Sample Data (for development/testing)
-- Uncomment to insert sample data

-- INSERT INTO users (user_id, user_metadata) VALUES
--     ('123e4567-e89b-12d3-a456-426614174000', '{"browser": "Chrome", "os": "Windows"}'),
--     ('123e4567-e89b-12d3-a456-426614174001', '{"browser": "Firefox", "os": "macOS"}');

-- INSERT INTO diagrams (user_id, s3_path, title, description, user_query, mermaid_code, status, version) VALUES
--     ('123e4567-e89b-12d3-a456-426614174000',
--      's3://diagram-maker-kb/users/123e4567-e89b-12d3-a456-426614174000/diagrams/d1.mmd',
--      'AWS Architecture Overview',
--      'High-level AWS infrastructure diagram',
--      'Show me AWS infrastructure for a web application',
--      'flowchart TD\n    A[User] --> B[CloudFront]\n    B --> C[EC2]',
--      'draft',
--      1);
