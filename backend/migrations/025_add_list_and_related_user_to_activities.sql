-- Add missing columns to activities table
ALTER TABLE activities ADD COLUMN list_id INTEGER REFERENCES lists(list_id);
ALTER TABLE activities ADD COLUMN related_user_id INTEGER REFERENCES users(user_id);
