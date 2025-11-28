from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from sqlalchemy import text
from ..database import get_db
from .. import models

router = APIRouter()


# ============ REVIEW LIKES ============

@router.post("/review/{review_id}/like")
def like_review(review_id: int, data: dict = Body(...), db: Session = Depends(get_db)):
    """
    Bir review'u beğen (like)
    İlk kez beğenilirse: review_likes tablosuna ekle
    Tekrar beğenilirse: review_likes tablosundan sil (toggle)
    """
    try:
        user_id = data.get("user_id")
        
        if not user_id:
            raise HTTPException(status_code=400, detail="user_id gerekli")
        
        # Review var mı?
        review = db.query(models.Review).filter(models.Review.review_id == review_id).first()
        if not review:
            raise HTTPException(status_code=404, detail="Yorum bulunamadı")
        
        # Kullanıcı bu review'u zaten beğenmişi mi?
        existing_like = db.query(models.ReviewLike).filter(
            models.ReviewLike.review_id == review_id,
            models.ReviewLike.user_id == user_id
        ).first()
        
        if existing_like:
            # Zaten beğenmişse, beğeniyi kaldır (toggle)
            db.delete(existing_like)
            db.commit()
            return {
                "success": True,
                "action": "unliked",
                "message": "Beğeni kaldırıldı",
                "review_id": review_id,
                "user_id": user_id
            }
        else:
            # Beğenmemişse, beğeniyi ekle
            new_like = models.ReviewLike(
                review_id=review_id,
                user_id=user_id
            )
            db.add(new_like)
            db.flush()  # Get the ID before commit
            
            # Activity kaydı oluştur
            activity = models.Activity(
                user_id=user_id,
                activity_type="like_review",
                review_id=review_id
            )
            db.add(activity)
            db.commit()
            db.refresh(new_like)
            
            return {
                "success": True,
                "action": "liked",
                "message": "Beğeni eklendi",
                "review_id": review_id,
                "user_id": user_id,
                "like_id": new_like.like_id
            }
    
    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/review/{review_id}/likes")
def get_review_likes(review_id: int, db: Session = Depends(get_db)):
    """
    Bir review'un kaç beğenisi var ve kim beğenmişi göster
    """
    try:
        # Review var mı?
        review = db.query(models.Review).filter(models.Review.review_id == review_id).first()
        if not review:
            raise HTTPException(status_code=404, detail="Yorum bulunamadı")
        
        # Beğenileri getir
        likes = db.query(models.ReviewLike).filter(
            models.ReviewLike.review_id == review_id
        ).all()
        
        # Beğenen kullanıcı bilgilerini getir
        likes_list = []
        for like in likes:
            user = db.query(models.User).filter(models.User.user_id == like.user_id).first()
            likes_list.append({
                "like_id": like.like_id,
                "user_id": like.user_id,
                "username": user.username if user else f"User {like.user_id}",
                "created_at": like.created_at
            })
        
        return {
            "success": True,
            "review_id": review_id,
            "total_likes": len(likes),
            "likes": likes_list
        }
    
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/review/{review_id}/liked-by-user/{user_id}")
def is_review_liked_by_user(review_id: int, user_id: int, db: Session = Depends(get_db)):
    """
    Kullanıcı bu review'u beğenmişi mi kontrolü
    """
    try:
        like = db.query(models.ReviewLike).filter(
            models.ReviewLike.review_id == review_id,
            models.ReviewLike.user_id == user_id
        ).first()
        
        return {
            "success": True,
            "review_id": review_id,
            "user_id": user_id,
            "is_liked": like is not None
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ REVIEW COMMENTS (Review Yorum yap) ============

@router.post("/review/{review_id}/comments")
def add_comment_to_review(review_id: int, data: dict = Body(...), db: Session = Depends(get_db)):
    """
    Bir review'a yorum ekle (review üzerine yorum)
    """
    try:
        user_id = data.get("user_id")
        comment_text = data.get("comment_text")
        
        if not user_id or not comment_text:
            raise HTTPException(status_code=400, detail="user_id ve comment_text gerekli")
        
        # Review var mı?
        review = db.query(models.Review).filter(models.Review.review_id == review_id).first()
        if not review:
            raise HTTPException(status_code=404, detail="Yorum bulunamadı")
        
        # Yorum ekle
        new_comment = models.ReviewComment(
            review_id=review_id,
            user_id=user_id,
            comment_text=comment_text
        )
        db.add(new_comment)
        db.flush()  # Get the ID before commit
        
        # Activity kaydı oluştur
        activity = models.Activity(
            user_id=user_id,
            activity_type="comment_review",
            review_id=review_id
        )
        db.add(activity)
        db.commit()
        db.refresh(new_comment)
        
        return {
            "success": True,
            "message": "Yorum eklendi",
            "review_id": review_id,
            "comment_id": new_comment.comment_id,
            "user_id": user_id,
            "comment_text": comment_text,
            "created_at": new_comment.created_at
        }
    
    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/review/{review_id}/comments")
def get_review_comments(review_id: int, db: Session = Depends(get_db)):
    """
    Bir review'a yapılan tüm yorumları getir
    """
    try:
        # Review var mı?
        review = db.query(models.Review).filter(models.Review.review_id == review_id).first()
        if not review:
            raise HTTPException(status_code=404, detail="Yorum bulunamadı")
        
        # Yorumları getir
        comments = db.query(models.ReviewComment).filter(
            models.ReviewComment.review_id == review_id
        ).order_by(models.ReviewComment.created_at.desc()).all()
        
        # Kullanıcı bilgilerini ekle
        comments_list = []
        for comment in comments:
            user = db.query(models.User).filter(models.User.user_id == comment.user_id).first()
            comments_list.append({
                "comment_id": comment.comment_id,
                "review_id": comment.review_id,
                "user_id": comment.user_id,
                "username": user.username if user else f"User {comment.user_id}",
                "avatar_url": user.avatar_url if user else None,
                "comment_text": comment.comment_text,
                "created_at": comment.created_at
            })
        
        return {
            "success": True,
            "review_id": review_id,
            "total_comments": len(comments),
            "comments": comments_list
        }
    
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/review-comments/{comment_id}")
def delete_review_comment(comment_id: int, data: dict = Body(...), db: Session = Depends(get_db)):
    """
    Bir review'a yapılan yorumu sil (sadece yorum sahibi silebilir)
    """
    try:
        user_id = data.get("user_id")
        
        if not user_id:
            raise HTTPException(status_code=400, detail="user_id gerekli")
        
        # Yorum var mı?
        comment = db.query(models.ReviewComment).filter(
            models.ReviewComment.comment_id == comment_id
        ).first()
        
        if not comment:
            raise HTTPException(status_code=404, detail="Yorum bulunamadı")
        
        # Sadece yorum sahibi silebilir
        if comment.user_id != user_id:
            raise HTTPException(status_code=403, detail="Sadece kendi yorumunuzu silebilirsiniz")
        
        db.delete(comment)
        db.commit()
        
        return {
            "success": True,
            "message": "Yorum silindi",
            "comment_id": comment_id
        }
    
    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# ============ ITEM LIKES ============

@router.post("/item/{item_id}/like")
def like_item(item_id: int, data: dict = Body(...), db: Session = Depends(get_db)):
    """
    Bir item'ı beğen (like)
    """
    try:
        user_id = data.get("user_id")
        
        if not user_id:
            raise HTTPException(status_code=400, detail="user_id gerekli")
        
        # Item var mı?
        item = db.query(models.Item).filter(models.Item.item_id == item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="İçerik bulunamadı")
        
        # Kullanıcı bu item'ı zaten beğenmişi mi?
        existing_like = db.query(models.ItemLike).filter(
            models.ItemLike.item_id == item_id,
            models.ItemLike.user_id == user_id
        ).first()
        
        if existing_like:
            # Zaten beğenmişse, beğeniyi kaldır
            db.delete(existing_like)
            db.commit()
            return {
                "success": True,
                "action": "unliked",
                "message": "Beğeni kaldırıldı",
                "item_id": item_id,
                "user_id": user_id
            }
        else:
            # Beğenmemişse, beğeniyi ekle
            new_like = models.ItemLike(
                item_id=item_id,
                user_id=user_id
            )
            db.add(new_like)
            db.flush()  # Get the ID before commit
            
            # Activity kaydı oluştur
            activity = models.Activity(
                user_id=user_id,
                activity_type="like_item",
                item_id=item_id
            )
            db.add(activity)
            db.commit()
            db.refresh(new_like)
            
            return {
                "success": True,
                "action": "liked",
                "message": "Beğeni eklendi",
                "item_id": item_id,
                "user_id": user_id,
                "like_id": new_like.like_id
            }
    
    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/item/{item_id}/likes")
def get_item_likes(item_id: int, db: Session = Depends(get_db)):
    """
    Bir item'ın kaç beğenisi var
    """
    try:
        item = db.query(models.Item).filter(models.Item.item_id == item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="İçerik bulunamadı")
        
        like_count = db.query(models.ItemLike).filter(
            models.ItemLike.item_id == item_id
        ).count()
        
        return {
            "success": True,
            "item_id": item_id,
            "total_likes": like_count
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
