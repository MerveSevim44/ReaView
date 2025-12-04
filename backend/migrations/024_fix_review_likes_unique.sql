-- Fix: review_likes ve review_comments'te UNIQUE constraint ekle
-- review_likes: bir kullanıcı bir review'u sadece bir kere beğenebilir

-- review_likes'te duplicate UNIQUE constraint varsa kaldır
ALTER TABLE review_likes DROP CONSTRAINT IF EXISTS review_likes_review_id_user_id_key;

-- Yeni UNIQUE constraint ekle
ALTER TABLE review_likes ADD CONSTRAINT review_likes_review_id_user_id_key UNIQUE (review_id, user_id);

-- review_comments'te duplicate constraint varsa kaldır
ALTER TABLE review_comments DROP CONSTRAINT IF EXISTS review_comments_pkey;
ALTER TABLE review_comments DROP CONSTRAINT IF EXISTS review_comments_review_id_user_id_key;

-- review_comments'e UNIQUE constraint ekle (bir kullanıcı review'a birden fazla yorum yapabilir, kısıtlama yok)
-- Ama NULL duplicate'leri varsa indexle çöz
ALTER TABLE review_comments ADD CONSTRAINT review_comments_pkey PRIMARY KEY (comment_id);

-- item_likes'te UNIQUE constraint
ALTER TABLE item_likes DROP CONSTRAINT IF EXISTS item_likes_item_id_user_id_key;
ALTER TABLE item_likes ADD CONSTRAINT item_likes_item_id_user_id_key UNIQUE (item_id, user_id);

-- Sequence'leri kontrol et ve düzelt (eğer varsa)
SELECT setval('review_likes_like_id_seq', (SELECT MAX(like_id) + 1 FROM review_likes), false);
SELECT setval('review_comments_comment_id_seq', (SELECT MAX(comment_id) + 1 FROM review_comments), false);
SELECT setval('item_likes_like_id_seq', (SELECT MAX(like_id) + 1 FROM item_likes), false);
