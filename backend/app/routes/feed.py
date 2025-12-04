from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from ..database import get_db

router = APIRouter()

@router.get("/")
def get_feed(
    user_id: int,
    skip: int = 0,
    limit: int = 15,
    db: Session = Depends(get_db)
):
    """
    Feed = takip edilen kullanıcıların aktiviteleri (activities tablosundan)
    Activity types: review, rating, follow, like_review, like_item, comment_review, list_add
    """
    
    query = text("""
        SELECT 
            a.activity_id,
            a.user_id,
            u.username,
            u.avatar_url,
            a.activity_type,
            a.item_id,
            a.review_id,
            a.list_id,
            a.related_user_id,
            a.created_at,
            -- Review/Item details (review veya rating için)
            CASE 
                WHEN a.activity_type = 'like_review' THEN COALESCE(ri.title, '')
                ELSE COALESCE(i.title, '')
            END AS title,
            CASE 
                WHEN a.activity_type = 'like_review' THEN COALESCE(ri.item_type, '')
                ELSE COALESCE(i.item_type, '')
            END AS item_type,
            CASE 
                WHEN a.activity_type = 'like_review' THEN COALESCE(ri.poster_url, '')
                ELSE COALESCE(i.poster_url, '')
            END AS poster_url,
            CASE 
                WHEN a.activity_type = 'like_review' THEN COALESCE(ri.year, 0)
                ELSE COALESCE(i.year, 0)
            END AS year,
            CASE 
                WHEN a.activity_type = 'like_review' THEN COALESCE(ri.description, '')
                ELSE COALESCE(i.description, '')
            END AS description,
            -- Review details (review ise)
            COALESCE(r.review_text, '') AS review_text,
            COALESCE(r.rating, 0) AS review_rating,
            -- Rating details (rating ise) - ratings tablosundan direct
            CASE 
                WHEN a.activity_type = 'rating' THEN COALESCE(rat.score, 0)
                ELSE 0
            END AS rating_score,
            -- Beğeni sayısı (review için)
            CASE
                WHEN a.activity_type IN ('review', 'like_review') THEN
                    COALESCE((SELECT COUNT(*) FROM review_likes WHERE review_id = a.review_id), 0)
                WHEN a.activity_type IN ('rating', 'like_item') THEN
                    COALESCE((SELECT COUNT(*) FROM item_likes WHERE item_id = a.item_id), 0)
                ELSE 0
            END AS like_count,
            -- Yorum sayısı
            COALESCE((SELECT COUNT(*) FROM review_comments WHERE review_id = a.review_id), 0) AS comment_count,
            -- Current user'ın beğenip beğenmediği (review için)
            CASE 
                WHEN a.activity_type IN ('review', 'like_review') THEN 
                    COALESCE((SELECT 1 FROM review_likes WHERE review_id = a.review_id AND user_id = :uid LIMIT 1), 0)
                ELSE 0
            END AS is_liked_by_user,
            -- Current user'ın beğenip beğenmediği (item için)
            CASE 
                WHEN a.activity_type IN ('rating', 'like_item') THEN 
                    COALESCE((SELECT 1 FROM item_likes WHERE item_id = a.item_id AND user_id = :uid LIMIT 1), 0)
                ELSE 0
            END AS is_item_liked_by_user
        FROM activities a
        JOIN users u ON u.user_id = a.user_id
        LEFT JOIN items i ON i.item_id = a.item_id
        LEFT JOIN reviews r ON r.review_id = a.review_id
        LEFT JOIN items ri ON ri.item_id = r.item_id
        LEFT JOIN ratings rat ON rat.user_id = a.user_id AND rat.item_id = a.item_id
        WHERE a.user_id IN (
            SELECT followee_id FROM follows WHERE follower_id = :uid
        )
        AND a.activity_type IN ('review', 'rating', 'like_review', 'like_item', 'comment_review')
        ORDER BY a.created_at DESC
        LIMIT :limit OFFSET :skip;
    """)

    result = db.execute(query, {"uid": user_id, "limit": limit, "skip": skip}).fetchall()
    return [dict(r._mapping) for r in result]
