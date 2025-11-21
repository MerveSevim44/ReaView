-- Add external_rating column to items table
-- Migration 003: Add external rating support for hybrid rating system
ALTER TABLE items ADD COLUMN external_rating INTEGER DEFAULT 0;
