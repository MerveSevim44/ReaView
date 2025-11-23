-- Create a function to get the next available review_id by finding gaps
-- This will reuse deleted IDs instead of always incrementing

CREATE OR REPLACE FUNCTION get_next_review_id()
RETURNS INTEGER AS $$
DECLARE
    next_id INTEGER;
BEGIN
    -- Find the smallest missing ID
    SELECT COALESCE(MIN(t.id), 1)
    INTO next_id
    FROM (
        SELECT GENERATE_SERIES(1, (SELECT COALESCE(MAX(review_id), 0) FROM reviews) + 1) AS id
    ) t
    WHERE t.id NOT IN (SELECT review_id FROM reviews);
    
    RETURN next_id;
END;
$$ LANGUAGE plpgsql;

-- Update the sequence to start from 1
DROP SEQUENCE IF EXISTS reviews_review_id_seq CASCADE;
CREATE SEQUENCE reviews_review_id_seq START WITH 1 INCREMENT BY 1;

-- Create a trigger to use the gap-filling function for new reviews
CREATE OR REPLACE FUNCTION set_review_id_on_insert()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.review_id IS NULL THEN
        NEW.review_id := get_next_review_id();
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Drop existing trigger if it exists
DROP TRIGGER IF EXISTS set_review_id_trigger ON reviews;

-- Create the trigger
CREATE TRIGGER set_review_id_trigger
BEFORE INSERT ON reviews
FOR EACH ROW
EXECUTE FUNCTION set_review_id_on_insert();

-- Update existing column to NOT use sequence default (we'll use trigger instead)
ALTER TABLE reviews ALTER COLUMN review_id DROP DEFAULT;
