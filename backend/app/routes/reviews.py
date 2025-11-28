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
    # Find the next available review_id (reuse deleted IDs)
    # Get all existing IDs
    existing_ids_query = db.query(models.Review.review_id).all()
    existing_ids = {row[0] for row in existing_ids_query}
    
    # Find the first available ID (starting from 1)
    next_id = 1
    while next_id in existing_ids:
        next_id += 1
    
    # Create review with the assigned ID
    new_review = models.Review(
        review_id=next_id,
        user_id=review.user_id,
        item_id=review.item_id,
        review_text=review.review_text,
        rating=review.rating
    )
    
    db.add(new_review)
    db.flush()  # Get the ID before commit
    
    # Activity kaydı oluştur
    activity = models.Activity(
        user_id=review.user_id,
        activity_type="review",
        item_id=review.item_id,
        review_id=new_review.review_id
    )
    db.add(activity)
    db.commit()
    db.refresh(new_review)
    
    # Get username
    user = db.query(models.User).filter(models.User.user_id == review.user_id).first()
    username = user.username if user else f"User {review.user_id}"
    
    review_dict = {
        "review_id": new_review.review_id,
        "user_id": new_review.user_id,
        "username": username,
        "item_id": new_review.item_id,
        "review_text": new_review.review_text,
        "rating": new_review.rating,
        "created_at": new_review.created_at
    }
    
    return schemas.ReviewOut(**review_dict)

# Yorum sil
@router.delete("/{review_id}")
def delete_review(review_id: int, db: Session = Depends(get_db)):
    """Yorum sil"""
    review = db.query(models.Review).filter(models.Review.review_id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Yorum bulunamadı")
    
    db.delete(review)
    db.commit()
    return {"message": "✅ Yorum başarıyla silindi", "review_id": review_id}


# ============================================
# RATINGS ENDPOINTS (ratings tablosu için)
# ============================================

@router.delete("/rating/{rating_id}")
def delete_rating(rating_id: int, db: Session = Depends(get_db)):
    """Puan sil"""
    try:
        print(f"🔴 DELETE /rating/{rating_id} başladı")
        
        rating = db.query(models.Rating).filter(models.Rating.rating_id == rating_id).first()
        if not rating:
            print(f"❌ Rating {rating_id} not found")
            raise HTTPException(status_code=404, detail="Puan bulunamadı")
        
        print(f"📝 Siliniyor: rating_id={rating_id}, user_id={rating.user_id}, item_id={rating.item_id}")
        
        db.delete(rating)
        db.commit()
        
        print(f"✅ Puan silindi: {rating_id}")
        return {"message": "✅ Puan başarıyla silindi", "rating_id": rating_id}
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Rating silme hatası: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Puan silme hatası: {str(e)}")

# Yorum güncelle
@router.put("/{review_id}", response_model=schemas.ReviewOut)
def update_review(
    review_id: int,
    review_update: schemas.ReviewUpdate,
    db: Session = Depends(get_db)
):
    """Yorum güncelle"""
    try:
        print(f"🔄 PUT /reviews/{review_id} başladı. Data: {review_update}")
        
        review = db.query(models.Review).filter(models.Review.review_id == review_id).first()
        if not review:
            print(f"❌ Review {review_id} not found")
            raise HTTPException(status_code=404, detail="Yorum bulunamadı")
        
        if review_update.review_text is not None:
            review.review_text = review_update.review_text
        if review_update.rating is not None and 1 <= review_update.rating <= 10:
            review.rating = review_update.rating
        
        db.commit()
        db.refresh(review)
        print(f"✅ Review {review_id} güncellendi")
        
        # Get username
        user = db.query(models.User).filter(models.User.user_id == review.user_id).first()
        username = user.username if user else f"User {review.user_id}"
        
        review_dict = {
            "review_id": review.review_id,
            "user_id": review.user_id,
            "username": username,
            "item_id": review.item_id,
            "review_text": review.review_text,
            "rating": review.rating,
            "created_at": review.created_at
        }
        
        return schemas.ReviewOut(**review_dict)
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ PUT Review hatası: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
