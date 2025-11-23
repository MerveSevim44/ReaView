-- Fix duplicate name columns in lists table
-- Drop the old list_name column and consolidate to just 'name'

BEGIN;

-- Drop indexes that reference list_name
DROP INDEX IF EXISTS idx_lists_name;

-- Drop the old list_name column (keep only 'name')
ALTER TABLE lists DROP COLUMN IF EXISTS list_name;

-- Ensure name column has NOT NULL constraint
ALTER TABLE lists ALTER COLUMN name SET NOT NULL;
ALTER TABLE lists ALTER COLUMN name SET DEFAULT 'Untitled';

COMMIT;
