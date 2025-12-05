from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from ..database import get_db
from .. import models, schemas
from .auth import verify_current_user
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
               u.username, 
               COALESCE(NULLIF(i.title, ''), NULLIF(i.title, 'Unknown'), '') AS title, 
               i.item_type, a.item_id, a.user_id,
               -- Review'a ait item başlığını da al (like_review ve comment_review için)
               COALESCE(NULLIF(i.title, ''), NULLIF(i.title, 'Unknown'), NULLIF(ri.title, ''), NULLIF(ri.title, 'Unknown'), '') AS title_resolved,
               a.review_id,
               -- Yorum yapılan review'un sahibinin username'i (comment_review ve like_review için)
               COALESCE(ru.username, '') AS review_owner_username,
               -- Yorum yapılan review'un text'i (comment_review ve like_review için)
               COALESCE(r.review_text, '') AS referenced_review_text,
               -- API items'in source_id'si (metadata referansı)
               COALESCE(r.source_id, '') AS source_id
        FROM activities a
        JOIN users u ON u.user_id = a.user_id
        LEFT JOIN items i ON i.item_id = a.item_id
        LEFT JOIN reviews r ON r.review_id = a.review_id
        LEFT JOIN items ri ON ri.item_id = r.item_id
        LEFT JOIN users ru ON ru.user_id = r.user_id
        WHERE a.user_id = :uid
        ORDER BY a.created_at DESC
        LIMIT 20
    """)
    rows = db.execute(q, {"uid": user_id}).fetchall()
    
    # Title'ı resolve et
    result = []
    for r in rows:
        row_dict = dict(r._mapping)
        # title_resolved kullan, yoksa title'ı kullan
        if row_dict.get('title_resolved'):
            row_dict['title'] = row_dict['title_resolved']
        result.append(row_dict)
    
    return result

# 4) Kullanıcı profilini güncelle (bio, avatar_url)
@router.put("/{user_id}", response_model=schemas.UserOut)
def update_user(user_id: int, user_update: schemas.UserUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(verify_current_user)):
    # Sadece kendi profilini güncelleyebilir
    if current_user.user_id != user_id:
        raise HTTPException(403, "Başka kullanıcının profilini güncelleyemezsiniz")
    
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not user:
        raise HTTPException(404, "Kullanıcı bulunamadı")
    
    # Güncelle
    if user_update.username is not None:
        # Check if username is already taken by another user
        existing = db.query(models.User).filter(
            models.User.username == user_update.username,
            models.User.user_id != user_id
        ).first()
        if existing:
            raise HTTPException(400, "Bu kullanıcı adı zaten kullanılıyor")
        user.username = user_update.username
    
    if user_update.email is not None:
        # Check if email is already taken by another user
        existing = db.query(models.User).filter(
            models.User.email == user_update.email,
            models.User.user_id != user_id
        ).first()
        if existing:
            raise HTTPException(400, "Bu e-posta adresi zaten kullanılıyor")
        user.email = user_update.email
    
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


# 6) Mevcut avatarları listele
@router.get("/api/avatars/list")
def list_avatars():
    """List all available avatars in the avatars directory"""
    from pathlib import Path
    avatars_dir = Path(__file__).parent.parent.parent / "avatars"
    
    if not avatars_dir.exists():
        return {"avatars": []}
    
    # Get all image files
    allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
    avatars = []
    
    for file_path in avatars_dir.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in allowed_extensions:
            avatars.append(file_path.name)
    
    # Sort alphabetically
    avatars.sort()
    
    return {"avatars": avatars}
