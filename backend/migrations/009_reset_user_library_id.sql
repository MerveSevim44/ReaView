-- Reset user_library sequence to start from 1
-- This ensures library_id starts from 1
-- PostgreSQL version

-- Reset the sequence WITHOUT truncating data
-- This preserves existing user_library records
ALTER SEQUENCE user_library_library_id_seq RESTART WITH 1;
