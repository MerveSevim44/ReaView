-- Migration 003: Add password_hash field to users table

-- Check if column exists before adding (to prevent errors if run multiple times)
-- SQLite doesn't have native IF NOT EXISTS for ALTER TABLE, so we add it directly
-- If it already exists, SQLite will throw an error which we can ignore

ALTER TABLE users ADD COLUMN password_hash VARCHAR(255) NOT NULL DEFAULT '';

-- Set default passwords for existing users (for backward compatibility)
-- In production, you would need to handle this differently
-- For now, set empty string as default (users would need to reset password)

-- Optional: If you want to mark old users as needing password reset:
-- ALTER TABLE users ADD COLUMN needs_password_reset BOOLEAN DEFAULT 1;
