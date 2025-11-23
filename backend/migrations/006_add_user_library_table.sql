-- Create user_library table for tracking user's read/watched status
CREATE TABLE IF NOT EXISTS user_library (
    library_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    item_id INTEGER NOT NULL REFERENCES items(item_id) ON DELETE CASCADE,
    status VARCHAR(20) NOT NULL CHECK (status IN ('read', 'toread', 'watched', 'towatch')),
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, item_id)
);

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_user_library_user_id ON user_library(user_id);
CREATE INDEX IF NOT EXISTS idx_user_library_status ON user_library(status);
