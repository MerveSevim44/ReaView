-- Migration 024: Activities table'ına review_id field'ı ekle
ALTER TABLE activities
ADD COLUMN review_id INTEGER REFERENCES reviews(review_id) ON DELETE CASCADE;

CREATE INDEX idx_activities_review_id ON activities(review_id);
