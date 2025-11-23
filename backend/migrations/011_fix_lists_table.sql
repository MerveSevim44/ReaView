-- Fix lists table - add missing columns
-- Migration 008'de eksik kalan sütunları ekle

-- Mevcut sütunları kontrol et ve eksik olanları ekle
ALTER TABLE lists ADD COLUMN IF NOT EXISTS name VARCHAR(255) NOT NULL DEFAULT 'Untitled';
ALTER TABLE lists ADD COLUMN IF NOT EXISTS description TEXT;
ALTER TABLE lists ADD COLUMN IF NOT EXISTS is_public INTEGER DEFAULT 0;
ALTER TABLE lists ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE lists ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- Index oluştur (eğer zaten yoksa)
CREATE INDEX IF NOT EXISTS idx_lists_user_id ON lists(user_id);
CREATE INDEX IF NOT EXISTS idx_lists_is_public ON lists(is_public);

-- lists_item tablosunu kontrol et
CREATE TABLE IF NOT EXISTS lists_item (
    list_item_id SERIAL PRIMARY KEY,
    list_id INTEGER NOT NULL REFERENCES lists(list_id) ON DELETE CASCADE,
    item_id INTEGER NOT NULL REFERENCES items(item_id) ON DELETE CASCADE,
    position INTEGER DEFAULT 0,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index'leri oluştur
CREATE INDEX IF NOT EXISTS idx_lists_item_list_id ON lists_item(list_id);
CREATE INDEX IF NOT EXISTS idx_lists_item_item_id ON lists_item(item_id);
