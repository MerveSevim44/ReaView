-- Create api_library table for tracking API items in user's library
-- This is for external content from TMDB, Google Books, etc.
CREATE TABLE IF NOT EXISTS api_library (
    library_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    source_id VARCHAR(100) NOT NULL,  -- 'tmdb_123', 'google_books_abc', vb.
    status VARCHAR(50) NOT NULL CHECK (status IN ('read', 'toread', 'watched', 'towatch')),
    title VARCHAR(255),
    item_type VARCHAR(20),  -- 'book' or 'movie'
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_api_library_user_id ON api_library(user_id);
CREATE INDEX IF NOT EXISTS idx_api_library_source_id ON api_library(source_id);
CREATE INDEX IF NOT EXISTS idx_api_library_status ON api_library(status);
