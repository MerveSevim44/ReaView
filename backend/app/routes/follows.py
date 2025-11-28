from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from ..database import get_db
from .. import models, schemas
from datetime import datetime

router = APIRouter()

@router.post("/{followee_id}/follow")
def follow_user(
    followee_id: int,
    follower_id: int = Query(..., description="Takip eden kullanıcı ID"),
    db: Session = Depends(get_db)
):
    """Bir kullanıcıyı takip et"""
    if follower_id == followee_id:
        raise HTTPException(status_code=400, detail="Kendi kendini takip edemezsin.")

    # Followee kullanıcısının var olup olmadığını kontrol et
    followee = db.query(models.User).filter(models.User.user_id == followee_id).first()
    if not followee:
        raise HTTPException(status_code=404, detail="Takip edilecek kullanıcı bulunamadı.")

    existing = db.query(models.Follow).filter(
        models.Follow.follower_id == follower_id,
        models.Follow.followee_id == followee_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Zaten takip ediyorsun.")

    follow = models.Follow(follower_id=follower_id, followee_id=followee_id, followed_at=datetime.utcnow())
    db.add(follow)
    db.flush()  # Get the ID before commit
    
    # Activity kaydı oluştur
    activity = models.Activity(
        user_id=follower_id,
        activity_type="follow",
        related_user_id=followee_id
    )
    db.add(activity)
    db.commit()
    db.refresh(follow)
    return {"message": "Takip edildi", "followee_id": followee_id, "follower_id": follower_id}


@router.delete("/{followee_id}/unfollow")
def unfollow_user(
    followee_id: int,
    follower_id: int = Query(..., description="Takip eden kullanıcı ID"),
    db: Session = Depends(get_db)
):
    """Bir kullanıcıyı takip etmeyi bırak"""
    record = db.query(models.Follow).filter(
        models.Follow.follower_id == follower_id,
        models.Follow.followee_id == followee_id
    ).first()
    if not record:
        raise HTTPException(status_code=404, detail="Takip kaydı bulunamadı.")
    db.delete(record)
    db.commit()
    return {"message": "Takipten çıkıldı", "followee_id": followee_id}


# Kullanıcının takip ettikleri
@router.get("/{user_id}/following")
def get_following(user_id: int, db: Session = Depends(get_db)):
    """Bir kullanıcının takip ettiği kişileri listele"""
    query = text("""
    SELECT u.user_id, u.username, u.email, u.bio, u.avatar_url, u.created_at
    FROM follows f
    JOIN users u ON f.followee_id = u.user_id
    WHERE f.follower_id = :uid
    ORDER BY u.username
    """)
    try:
        result = db.execute(query, {"uid": user_id}).fetchall()
        return [dict(r._mapping) if hasattr(r, '_mapping') else dict(r) for r in result]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Takip listesi alınamadı: {str(e)}")

# Kullanıcının takipçileri
@router.get("/{user_id}/followers")
def get_followers(user_id: int, db: Session = Depends(get_db)):
    """Bir kullanıcının takipçilerini listele"""
    query = text("""
    SELECT u.user_id, u.username, u.email, u.bio, u.avatar_url, u.created_at
    FROM follows f
    JOIN users u ON f.follower_id = u.user_id
    WHERE f.followee_id = :uid
    ORDER BY u.username
    """)
    try:
        result = db.execute(query, {"uid": user_id}).fetchall()
        return [dict(r._mapping) if hasattr(r, '_mapping') else dict(r) for r in result]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Takipçiler alınamadı: {str(e)}")


@router.get("/{user_id}/follow-stats")
def get_follow_stats(user_id: int, db: Session = Depends(get_db)):
    """Bir kullanıcının takip istatistiklerini getir"""
    following_count = db.query(models.Follow).filter(
        models.Follow.follower_id == user_id
    ).count()
    
    followers_count = db.query(models.Follow).filter(
        models.Follow.followee_id == user_id
    ).count()
    
    return {
        "user_id": user_id,
        "following_count": following_count,
        "followers_count": followers_count
    }


@router.get("/{user_id}/is-following/{target_user_id}")
def is_following(user_id: int, target_user_id: int, db: Session = Depends(get_db)):
    """Bir kullanıcının başka bir kullanıcıyı takip edip etmediğini kontrol et"""
    record = db.query(models.Follow).filter(
        models.Follow.follower_id == user_id,
        models.Follow.followee_id == target_user_id
    ).first()
    
    return {"is_following": record is not None}

