-- Reset review sequence to always start from 1
-- When reviews are deleted, the next new review will reuse the deleted ID
-- This ensures IDs are always compact (1, 2, 3... without gaps)

-- Step 1: Create or reset the sequence to 1
DROP SEQUENCE IF EXISTS reviews_review_id_seq CASCADE;
CREATE SEQUENCE reviews_review_id_seq START WITH 1;

-- Step 2: Update the column to use the sequence
ALTER TABLE reviews ALTER COLUMN review_id SET DEFAULT nextval('reviews_review_id_seq');

-- Step 3: Link the sequence to the column
ALTER SEQUENCE reviews_review_id_seq OWNED BY reviews.review_id;
