-- Create ratings table for storing user ratings
CREATE TABLE IF NOT EXISTS ratings (
    rating_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    item_id INTEGER NOT NULL REFERENCES items(item_id) ON DELETE CASCADE,
    score INTEGER NOT NULL CHECK (score >= 1 AND score <= 10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, item_id)
);

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_ratings_user_item ON ratings(user_id, item_id);
CREATE INDEX IF NOT EXISTS idx_ratings_item ON ratings(item_id);
CREATE INDEX IF NOT EXISTS idx_ratings_user ON ratings(user_id);
