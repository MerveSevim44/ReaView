from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from ..database import get_db
from .. import models, schemas

router = APIRouter()

# 1) Tek kullanıcı bilgisi
@router.get("/{user_id}", response_model=schemas.UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not user:
        raise HTTPException(404, "Kullanıcı bulunamadı")
    return user

# 2) Kullanıcının yorumları (son 20)
@router.get("/{user_id}/reviews", response_model=list[schemas.ReviewOut])
def get_user_reviews(user_id: int, db: Session = Depends(get_db)):
    return (
        db.query(models.Review)
        .filter(models.Review.user_id == user_id)
        .order_by(models.Review.created_at.desc())
        .limit(20)
        .all()
    )

# 3) Kullanıcının aktiviteleri (join’li, son 20)
@router.get("/{user_id}/activities")
def get_user_activities(user_id: int, db: Session = Depends(get_db)):
    q = text("""
        SELECT a.activity_id, a.activity_type, a.created_at,
               u.username, i.title, i.item_type, a.item_id, a.user_id
        FROM activities a
        JOIN users u ON u.user_id = a.user_id
        LEFT JOIN items i ON i.item_id = a.item_id
        WHERE a.user_id = :uid
        ORDER BY a.created_at DESC
        LIMIT 20
    """)
    rows = db.execute(q, {"uid": user_id}).fetchall()
    return [dict(r._mapping) for r in rows]
