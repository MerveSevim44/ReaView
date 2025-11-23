-- Reset lists sequence to 1 so new lists start from 1
-- This ensures that when a list is deleted, the next list created starts from 1
-- The delete endpoint will handle sequence management on each deletion

SELECT setval('lists_list_id_seq', 1, false);
