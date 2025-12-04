-- Fix user_library sequence and remove duplicates
DELETE FROM user_library WHERE library_id IN (
  SELECT library_id FROM user_library 
  WHERE (user_id, item_id, status) IN (
    SELECT user_id, item_id, status FROM user_library 
    GROUP BY user_id, item_id, status HAVING COUNT(*) > 1
  ) AND library_id NOT IN (
    SELECT MIN(library_id) FROM user_library 
    GROUP BY user_id, item_id, status HAVING COUNT(*) > 1
  )
);

-- Reset sequence
SELECT setval('user_library_library_id_seq', (SELECT MAX(library_id) FROM user_library));

-- Add unique constraint if not exists
ALTER TABLE user_library DROP CONSTRAINT IF EXISTS user_library_user_id_item_id_status_key;
ALTER TABLE user_library ADD CONSTRAINT user_library_user_id_item_id_status_key UNIQUE (user_id, item_id, status);
