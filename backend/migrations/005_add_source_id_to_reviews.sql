-- Add source_id column to reviews table for API items
-- Make item_id nullable (API items don't have item_id)

ALTER TABLE reviews
ADD COLUMN source_id VARCHAR(100) NULL;

-- Make item_id nullable since API items won't have item_id
ALTER TABLE reviews
ALTER COLUMN item_id DROP NOT NULL;

-- Create index on source_id for faster lookups
CREATE INDEX idx_reviews_source_id ON reviews(source_id);
