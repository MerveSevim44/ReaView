-- Create lists table for custom user lists
CREATE TABLE IF NOT EXISTS lists (
    list_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    is_public INTEGER DEFAULT 0,  -- 0=private, 1=public
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create lists_item table for items in custom lists (many-to-many)
CREATE TABLE IF NOT EXISTS lists_item (
    list_item_id SERIAL PRIMARY KEY,
    list_id INTEGER NOT NULL REFERENCES lists(list_id) ON DELETE CASCADE,
    item_id INTEGER NOT NULL REFERENCES items(item_id) ON DELETE CASCADE,
    position INTEGER DEFAULT 0,  -- For ordering
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_lists_user_id ON lists(user_id);
CREATE INDEX IF NOT EXISTS idx_lists_is_public ON lists(is_public);
CREATE INDEX IF NOT EXISTS idx_lists_item_list_id ON lists_item(list_id);
CREATE INDEX IF NOT EXISTS idx_lists_item_item_id ON lists_item(item_id);
