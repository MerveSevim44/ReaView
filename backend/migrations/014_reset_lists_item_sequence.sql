-- Reset lists_item sequence to 1 so new list items start from 1
-- This ensures that when items are removed from lists, new items start from 1
-- The delete endpoint will handle sequence management on each deletion

SELECT setval('lists_item_list_item_id_seq', 1, false);
