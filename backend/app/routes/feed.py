from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from ..database import get_db
from .auth import verify_current_user
from .. import models
import requests
import os

router = APIRouter()

def enrich_poster_if_missing(poster_url: str, title: str, external_api_source: str, external_api_id: str) -> str:
    """
    If poster_url is empty, try to fetch it from external APIs
    """
    if poster_url and poster_url.strip():
        return poster_url
    
    # Try to fetch from TMDB if it's a movie
    if external_api_source == 'tmdb' and external_api_id:
        try:
            api_key = os.getenv("API_KEY")
            if api_key:
                url = f"https://api.themoviedb.org/3/movie/{external_api_id}"
                r = requests.get(url, params={"api_key": api_key}, timeout=3)
                if r.status_code == 200:
                    data = r.json()
                    poster_path = data.get('poster_path')
                    if poster_path:
                        return f"https://image.tmdb.org/t/p/w500{poster_path}"
        except Exception as e:
            print(f"Error enriching TMDB poster: {e}")
    
    # If still no poster and we have a title, try to search
    if title:
        try:
            api_key = os.getenv("API_KEY")
            if api_key and external_api_source == 'tmdb':
                params = {"api_key": api_key, "query": title}
                r = requests.get("https://api.themoviedb.org/3/search/movie", params=params, timeout=3)
                if r.status_code == 200:
                    results = r.json().get("results", [])
                    if results and results[0].get("poster_path"):
                        return f"https://image.tmdb.org/t/p/w500{results[0]['poster_path']}"
        except Exception as e:
            print(f"Error searching for poster: {e}")
    
    return poster_url

@router.get("/debug/items-with-posters")
def debug_items_with_posters(db: Session = Depends(get_db)):
    """
    Debug endpoint - check if items have poster_url data
    """
    try:
        from sqlalchemy import text as sql_text
        query = sql_text("""
            SELECT item_id, title, poster_url, external_api_source
            FROM items
            LIMIT 20
        """)
        result = db.execute(query).fetchall()
        return {
            "total_items": len(result),
            "items": [dict(r._mapping) if hasattr(r, '_mapping') else dict(zip(['item_id', 'title', 'poster_url', 'external_api_source'], r)) for r in result]
        }
    except Exception as e:
        return {"error": str(e)}

@router.get("/")
def get_feed(
    skip: int = 0,
    limit: int = 15,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(verify_current_user)
):
    """
    Feed = takip edilen kullanıcıların aktiviteleri (activities tablosundan)
    Activity types: review, rating, follow, like_review, like_item, comment_review, list_add
    
    user_id artık token'dan otomatik alınıyor
    """
    
    user_id = current_user.user_id
    
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
                WHEN a.activity_type = 'like_review' THEN COALESCE(NULLIF(ri.title, ''), NULLIF(ri.title, 'Unknown'), '')
                ELSE COALESCE(NULLIF(i.title, ''), NULLIF(i.title, 'Unknown'), '')
            END AS title,
            CASE 
                WHEN a.activity_type = 'like_review' THEN COALESCE(ri.item_type, '')
                ELSE COALESCE(i.item_type, '')
            END AS item_type,
            CASE 
                WHEN a.activity_type = 'like_review' THEN NULLIF(ri.poster_url, '')
                ELSE NULLIF(i.poster_url, '')
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
            END AS is_item_liked_by_user,
            -- Yorum yapılan review'un sahibinin username'i (comment_review ve like_review için)
            COALESCE(ru.username, '') AS review_owner_username,
            -- Yorum yapılan review'un text'i (comment_review ve like_review için)
            COALESCE(r.review_text, '') AS referenced_review_text,
            -- API items'in source_id'si (metadata referansı)
            COALESCE(r.source_id, '') AS source_id,
            -- External API info for poster enrichment
            CASE 
                WHEN a.activity_type = 'like_review' THEN COALESCE(ri.external_api_source, '')
                ELSE COALESCE(i.external_api_source, '')
            END AS external_api_source,
            CASE 
                WHEN a.activity_type = 'like_review' THEN COALESCE(ri.external_api_id, '')
                ELSE COALESCE(i.external_api_id, '')
            END AS external_api_id
        FROM activities a
        JOIN users u ON u.user_id = a.user_id
        LEFT JOIN items i ON i.item_id = a.item_id
        LEFT JOIN reviews r ON r.review_id = a.review_id
        LEFT JOIN items ri ON ri.item_id = r.item_id
        LEFT JOIN ratings rat ON rat.user_id = a.user_id AND rat.item_id = a.item_id
        LEFT JOIN users ru ON ru.user_id = r.user_id
        WHERE a.user_id IN (
            SELECT followee_id FROM follows WHERE follower_id = :uid
        )
        AND a.activity_type IN ('review', 'rating', 'like_review', 'like_item', 'comment_review')
        ORDER BY a.created_at DESC
        LIMIT :limit OFFSET :skip;
    """)

    result = db.execute(query, {"uid": user_id, "limit": limit, "skip": skip}).fetchall()
    activities = [dict(r._mapping) for r in result]
    
    # Enrich poster_url if missing
    for activity in activities:
        if not activity.get('poster_url') or activity['poster_url'] == '':
            poster = enrich_poster_if_missing(
                activity.get('poster_url', ''),
                activity.get('title', ''),
                activity.get('external_api_source', ''),
                activity.get('external_api_id', '')
            )
            activity['poster_url'] = poster
    
    return activities
