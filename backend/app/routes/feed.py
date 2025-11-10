from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from ..database import get_db
from .. import models, schemas

router = APIRouter()

@router.get("/", response_model=list[schemas.ActivityOut])
def get_feed(db: Session = Depends(get_db)):
    # Query activities with IDs only (matches ActivityOut schema)
    query = text("""
    SELECT 
        a.activity_id,
        a.activity_type,
        a.user_id,
        a.item_id,
        a.created_at
    FROM activities a
    ORDER BY a.created_at DESC
    LIMIT 20
    """)
    result = db.execute(query).fetchall()
    # Convert rows to dicts (works with SQLAlchemy 2.0)
    return [dict(row._mapping) if hasattr(row, '_mapping') else dict(row) for row in result]


@router.get("/detailed", response_model=list[schemas.ActivityWithDetailsOut])
def get_feed_detailed(db: Session = Depends(get_db)):
    # Query activities with user and item details (for a richer feed display)
    query = text("""
    SELECT 
        a.activity_id,
        a.activity_type,
        a.created_at,
        u.username,
        i.title,
        i.description as item_type
    FROM activities a
    JOIN users u ON u.user_id = a.user_id
    LEFT JOIN items i ON i.item_id = a.item_id
    ORDER BY a.created_at DESC
    LIMIT 20
    """)
    result = db.execute(query).fetchall()
    return [dict(row._mapping) if hasattr(row, '_mapping') else dict(row) for row in result]

