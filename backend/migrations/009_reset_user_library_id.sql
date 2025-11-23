-- Reset user_library sequence to start from 1
-- This ensures library_id starts from 1
-- PostgreSQL version

-- Truncate the table and reset the sequence
TRUNCATE TABLE user_library CASCADE;
ALTER SEQUENCE user_library_library_id_seq RESTART WITH 1;
