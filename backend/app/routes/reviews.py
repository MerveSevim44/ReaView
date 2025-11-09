from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas

router = APIRouter()

# Tüm yorumları listele
@router.get("/", response_model=list[schemas.ReviewOut])
def get_reviews(db: Session = Depends(get_db)):
    return db.query(models.Review).order_by(models.Review.created_at.desc()).limit(20).all()

# Belirli bir item'a ait yorumları getir
@router.get("/item/{item_id}", response_model=list[schemas.ReviewOut])
def get_reviews_for_item(item_id: int, db: Session = Depends(get_db)):
    return db.query(models.Review).filter(models.Review.item_id == item_id).order_by(models.Review.created_at.desc()).all()

# Yeni yorum oluştur
@router.post("/", response_model=schemas.ReviewOut)
def create_review(review: schemas.ReviewCreate, db: Session = Depends(get_db)):
    new_review = models.Review(**review.dict())
    db.add(new_review)
    db.commit()
    db.refresh(new_review)
    return new_review
