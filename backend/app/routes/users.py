from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from ..database import get_db
from .. import models, schemas
from .auth import get_current_user
import os

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

# 3) Kullanıcının aktiviteleri (join'li, son 20)
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

# 4) Kullanıcı profilini güncelle (bio, avatar_url)
@router.put("/{user_id}", response_model=schemas.UserOut)
def update_user(user_id: int, user_update: schemas.UserUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # Sadece kendi profilini güncelleyebilir
    if current_user.user_id != user_id:
        raise HTTPException(403, "Başka kullanıcının profilini güncelleyemezsiniz")
    
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not user:
        raise HTTPException(404, "Kullanıcı bulunamadı")
    
    # Güncelle
    if user_update.bio is not None:
        user.bio = user_update.bio
    if user_update.avatar_url is not None:
        user.avatar_url = user_update.avatar_url
    
    db.commit()
    db.refresh(user)
    return user


# 5) Avatar resim serve et (static files)
@router.get("/avatars/{filename}")
def serve_avatar(filename: str):
    """Serve avatar images from avatars directory"""
    from pathlib import Path
    avatars_dir = Path(__file__).parent.parent.parent / "avatars"
    file_path = avatars_dir / filename
    
    # Security: prevent directory traversal
    if not str(file_path).startswith(str(avatars_dir)):
        raise HTTPException(403, "Access denied")
    
    if not file_path.exists():
        raise HTTPException(404, "Avatar not found")
    
    return FileResponse(file_path)
