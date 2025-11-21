from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from ..database import get_db
from .. import models, schemas

router = APIRouter()

# Tüm yorumları listele
@router.get("/", response_model=list[schemas.ReviewOut])
def get_reviews(db: Session = Depends(get_db)):
    # Join reviews with users to get username
    query = text("""
        SELECT r.review_id, r.user_id, r.item_id, r.review_text, r.rating, r.created_at, u.username
        FROM reviews r
        LEFT JOIN users u ON r.user_id = u.user_id
        ORDER BY r.created_at DESC
        LIMIT 20
    """)
    result = db.execute(query).fetchall()
    return [dict(r._mapping) for r in result]

# Belirli bir item'a ait yorumları getir
@router.get("/item/{item_id}", response_model=list[schemas.ReviewOut])
def get_reviews_for_item(item_id: int, db: Session = Depends(get_db)):
    # Join reviews with users to get username
    query = text("""
        SELECT r.review_id, r.user_id, r.item_id, r.review_text, r.rating, r.created_at, u.username
        FROM reviews r
        LEFT JOIN users u ON r.user_id = u.user_id
        WHERE r.item_id = :item_id
        ORDER BY r.created_at DESC
    """)
    result = db.execute(query, {"item_id": item_id}).fetchall()
    return [dict(r._mapping) for r in result]

# Yeni yorum oluştur
@router.post("/", response_model=schemas.ReviewOut)
def create_review(review: schemas.ReviewCreate, db: Session = Depends(get_db)):
    new_review = models.Review(**review.dict())
    db.add(new_review)
    db.commit()
    db.refresh(new_review)
    return new_review

# Yorum sil
@router.delete("/{review_id}")
def delete_review(review_id: int, db: Session = Depends(get_db)):
    """Yorum sil"""
    review = db.query(models.Review).filter(models.Review.review_id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Yorum bulunamadı")
    
    db.delete(review)
    db.commit()
    return {"message": "Yorum başarıyla silindi"}

# Yorum güncelle
@router.put("/{review_id}")
def update_review(
    review_id: int,
    review_text: str = None,
    rating: int = None,
    db: Session = Depends(get_db)
):
    """Yorum güncelle"""
    review = db.query(models.Review).filter(models.Review.review_id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Yorum bulunamadı")
    
    if review_text is not None:
        review.review_text = review_text
    if rating is not None and 1 <= rating <= 5:
        review.rating = rating
    
    db.commit()
    db.refresh(review)
    return review
