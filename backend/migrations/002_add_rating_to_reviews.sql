-- Add rating column to reviews table
ALTER TABLE reviews ADD COLUMN rating INTEGER DEFAULT 5;
