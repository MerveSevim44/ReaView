from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from ..database import get_db
from .. import models, schemas

router = APIRouter()

@router.get("/", response_model=list[schemas.ActivityOut])
def get_feed(db: Session = Depends(get_db)):
    # Query activities with joins; using text() for raw SQL
    query = text("""
    SELECT a.activity_id, a.activity_type, a.created_at,
           a.user_id, a.item_id
    FROM activities a
    ORDER BY a.created_at DESC
    LIMIT 20
    """)
    result = db.execute(query).fetchall()
    # Convert rows to dicts (works with SQLAlchemy 2.0)
    return [dict(row._mapping) if hasattr(row, '_mapping') else dict(row) for row in result]

