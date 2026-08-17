-- Migration: Update list privacy levels
-- Date: 2025-12-05
-- Description: Change is_public to privacy_level with more granular control

-- Add new privacy_level column
-- 0 = private (sadece ben)
-- 1 = followers (sadece takipçilerim)
-- 2 = public (herkes)
ALTER TABLE lists ADD COLUMN IF NOT EXISTS privacy_level INTEGER DEFAULT 0;

-- Migrate existing data: is_public=1 -> privacy_level=2, is_public=0 -> privacy_level=0
UPDATE lists SET privacy_level = CASE 
    WHEN is_public = 1 THEN 2 
    ELSE 0 
END WHERE privacy_level IS NULL OR privacy_level = 0;
