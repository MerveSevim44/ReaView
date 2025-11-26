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
    Feed = takip edilen kullanıcıların review + rating aktiviteleri
    """
    
    query = text("""
        (
            -- REVIEW aktiviteleri
            SELECT 
                r.user_id,
                u.username,
                u.avatar_url,
                r.item_id,
                i.title,
                i.item_type,
                i.poster_url,
                i.year,
                r.review_text,
                r.rating AS rating_score,
                r.created_at,
                'review' AS activity_type
            FROM reviews r
            JOIN users u ON u.user_id = r.user_id
            JOIN items i ON i.item_id = r.item_id
            WHERE r.user_id IN (
                SELECT followee_id FROM follows WHERE follower_id = :uid
            )
        )
        UNION ALL
        (
            -- RATING aktiviteleri
            SELECT 
                rt.user_id,
                u.username,
                u.avatar_url,
                rt.item_id,
                i.title,
                i.item_type,
                i.poster_url,
                i.year,
                '' AS review_text,
                rt.score AS rating_score,
                rt.created_at,
                'rating' AS activity_type
            FROM ratings rt
            JOIN users u ON u.user_id = rt.user_id
            JOIN items i ON i.item_id = rt.item_id
            WHERE rt.user_id IN (
                SELECT followee_id FROM follows WHERE follower_id = :uid
            )
        )
        ORDER BY created_at DESC
        LIMIT :limit OFFSET :skip;
    """)

    result = db.execute(query, {"uid": user_id, "limit": limit, "skip": skip}).fetchall()
    return [dict(r._mapping) for r in result]

