-- Create review_comments table for storing user comments on reviews
CREATE TABLE IF NOT EXISTS review_comments (
    comment_id SERIAL PRIMARY KEY,
    review_id INTEGER NOT NULL REFERENCES reviews(review_id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    comment_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for faster lookups
CREATE INDEX IF NOT EXISTS idx_review_comments_review_id ON review_comments(review_id);
CREATE INDEX IF NOT EXISTS idx_review_comments_user_id ON review_comments(user_id);
CREATE INDEX IF NOT EXISTS idx_review_comments_created_at ON review_comments(created_at);
