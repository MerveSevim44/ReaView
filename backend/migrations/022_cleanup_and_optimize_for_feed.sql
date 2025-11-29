-- Clean up database schema for Feed optimization
-- Drop redundant activity-specific tables

DROP TABLE IF EXISTS activity_follows CASCADE;
DROP TABLE IF EXISTS activity_likes_item CASCADE;
DROP TABLE IF EXISTS activity_likes_review CASCADE;
DROP TABLE IF EXISTS activity_list_adds CASCADE;
DROP TABLE IF EXISTS activity_ratings CASCADE;
DROP TABLE IF EXISTS activity_reviews CASCADE;

-- Recreate activities table with better structure for feed
-- Use CREATE TABLE IF NOT EXISTS to preserve existing data
CREATE TABLE IF NOT EXISTS activities (
    activity_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    activity_type VARCHAR(50) NOT NULL,
    item_id INTEGER REFERENCES items(item_id) ON DELETE CASCADE,
    review_id INTEGER REFERENCES reviews(review_id) ON DELETE CASCADE,
    list_id INTEGER REFERENCES lists(list_id) ON DELETE CASCADE,
    related_user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_activities_user_id ON activities(user_id);
CREATE INDEX IF NOT EXISTS idx_activities_created_at ON activities(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_activities_type ON activities(activity_type);
CREATE INDEX IF NOT EXISTS idx_activities_user_created ON activities(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_activities_item_id ON activities(item_id);
CREATE INDEX IF NOT EXISTS idx_activities_review_id ON activities(review_id);
CREATE INDEX IF NOT EXISTS idx_activities_related_user ON activities(related_user_id);

CREATE INDEX IF NOT EXISTS idx_reviews_user_created ON reviews(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_ratings_user_created ON ratings(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_follows_follower ON follows(follower_id);
CREATE INDEX IF NOT EXISTS idx_follows_followee ON follows(followee_id);
CREATE INDEX IF NOT EXISTS idx_review_likes_review ON review_likes(review_id);
CREATE INDEX IF NOT EXISTS idx_item_likes_item ON item_likes(item_id);
CREATE INDEX IF NOT EXISTS idx_user_library_user ON user_library(user_id, status);

ALTER TABLE activities 
ADD CONSTRAINT check_activity_type 
CHECK (activity_type IN ('review', 'rating', 'follow', 'like_review', 'like_item', 'list_add'));
