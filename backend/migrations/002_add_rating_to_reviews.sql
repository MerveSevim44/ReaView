-- Add rating column to reviews table
ALTER TABLE reviews ADD COLUMN IF NOT EXISTS rating INTEGER DEFAULT 10;
