-- Fix review_likes sequence to start from 4
SELECT setval('review_likes_like_id_seq', 4, false);
