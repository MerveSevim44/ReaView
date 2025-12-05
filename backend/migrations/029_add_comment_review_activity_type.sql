-- Add comment_review to allowed activity types
-- First, drop the old constraint
ALTER TABLE activities DROP CONSTRAINT IF EXISTS check_activity_type;

-- Add the new constraint with comment_review included
ALTER TABLE activities 
ADD CONSTRAINT check_activity_type 
CHECK (activity_type IN ('review', 'rating', 'follow', 'like_review', 'like_item', 'comment_review', 'list_add'));
