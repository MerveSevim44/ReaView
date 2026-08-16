-- Reset reviews and ratings sequences to max(id) + 1 to prevent UniqueViolation errors
-- This fixes the issue where manual ID assignment caused sequence to be out of sync

SELECT setval('reviews_review_id_seq', COALESCE((SELECT MAX(review_id) FROM reviews), 0) + 1, false);
SELECT setval('ratings_rating_id_seq', COALESCE((SELECT MAX(rating_id) FROM ratings), 0) + 1, false);
