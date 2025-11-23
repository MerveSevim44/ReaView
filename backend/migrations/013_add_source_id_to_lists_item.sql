-- Migration 013: Add source_id column to lists_item table for API items support
-- This allows both database items (item_id) and API items (source_id) to be added to custom lists
-- with proper duplicate prevention

ALTER TABLE lists_item ADD COLUMN IF NOT EXISTS source_id VARCHAR(100);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_lists_item_source_id ON lists_item(list_id, source_id);
