from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text, desc, func
from ..database import get_db
from .. import models, schemas
from ..services.external_api import get_tmdb_reviews, get_google_books_reviews

router = APIRouter()


def calculate_hybrid_rating(item_id: int, item: models.Item, db: Session):
    """
    İçerik için hybrid rating hesapla:
    - external_rating: API'den gelen rating
    - user_rating: Kullanıcı reviews'lerinden
    - combined_rating: İkisinin ortalaması
    """
    # User reviews'ten rating hesapla
    rating_query = text("""
        SELECT AVG(rating) as avg_rating, COUNT(*) as total_ratings
        FROM reviews
        WHERE item_id = :item_id AND rating IS NOT NULL
    """)
    rating_result = db.execute(rating_query, {"item_id": item_id}).first()
    
    user_rating = round(rating_result[0], 1) if rating_result[0] else 0
    review_count = rating_result[1] or 0
    
    # External rating (API'den)
    external_rating = item.external_rating or 0
    
    # Combined rating (ortalama)
    if external_rating > 0 and user_rating > 0:
        combined_rating = round((external_rating + user_rating) / 2, 1)
    elif external_rating > 0:
        combined_rating = external_rating
    else:
        combined_rating = user_rating
    
    return {
        "external_rating": external_rating,
        "user_rating": user_rating,
        "combined_rating": combined_rating,
        "review_count": review_count,
        "popularity": review_count  # Popularity = review count
    }


# ============================================
# 1️⃣ SPECIAL ROUTES (Sabit route'lar BAŞTA)
# ============================================

# 🔍 Arama
@router.get("/search", response_model=list[schemas.ItemOut])
def search_items(
    q: str = Query(..., min_length=2, description="Arama metni"),
    item_type: str = Query(None, description="'book' veya 'movie'"),
    db: Session = Depends(get_db)
):
    """İçerik ara (başlık/açıklama)"""
    query = db.query(models.Item)
    
    # Başlık veya açıklamada ara
    query = query.filter(
        (models.Item.title.ilike(f"%{q}%")) |
        (models.Item.description.ilike(f"%{q}%"))
    )
    
    # item_type filtresi
    if item_type:
        query = query.filter(models.Item.item_type == item_type)
    
    items = query.limit(20).all()
    
    result = []
    for item in items:
        rating_info = calculate_hybrid_rating(item.item_id, item, db)
        item_dict = {
            "item_id": item.item_id,
            "title": item.title,
            "description": item.description,
            "item_type": item.item_type,
            "year": item.year,
            "poster_url": item.poster_url,
            "external_api_id": item.external_api_id,
            "external_api_source": item.external_api_source,
            "genres": item.genres,
            "authors": item.authors,
            "director": item.director,
            "actors": item.actors,
            "page_count": item.page_count,
            "created_at": item.created_at,
            **rating_info
        }
        result.append(item_dict)
    
    return result


# 🔥 En Yüksek Puanlılar
@router.get("/featured/top-rated", response_model=list[schemas.ItemOut])
def get_top_rated(limit: int = Query(6, ge=1, le=50), db: Session = Depends(get_db)):
    """En yüksek puanlı içerikleri getir"""
    items = db.query(models.Item).filter(
        models.Item.external_rating > 0
    ).order_by(desc(models.Item.external_rating)).limit(limit).all()
    
    result = []
    for item in items:
        rating_info = calculate_hybrid_rating(item.item_id, item, db)
        item_dict = {
            "item_id": item.item_id,
            "title": item.title,
            "description": item.description,
            "item_type": item.item_type,
            "year": item.year,
            "poster_url": item.poster_url,
            "external_api_id": item.external_api_id,
            "external_api_source": item.external_api_source,
            "genres": item.genres,
            "authors": item.authors,
            "director": item.director,
            "actors": item.actors,
            "page_count": item.page_count,
            "created_at": item.created_at,
            **rating_info
        }
        result.append(item_dict)
    
    return result


# 👥 En Popülerler (En çok review alanlar)
@router.get("/featured/popular", response_model=list[schemas.ItemOut])
def get_popular(limit: int = Query(6, ge=1, le=50), db: Session = Depends(get_db)):
    """En popüler içerikleri getir (en çok review alan)"""
    # Reviews count'a göre sırala
    subquery = db.query(
        models.Review.item_id,
        func.count(models.Review.review_id).label('review_count')
    ).group_by(models.Review.item_id).subquery()
    
    items = db.query(models.Item).outerjoin(
        subquery,
        models.Item.item_id == subquery.c.item_id
    ).order_by(desc(func.coalesce(subquery.c.review_count, 0))).limit(limit).all()
    
    result = []
    for item in items:
        rating_info = calculate_hybrid_rating(item.item_id, item, db)
        item_dict = {
            "item_id": item.item_id,
            "title": item.title,
            "description": item.description,
            "item_type": item.item_type,
            "year": item.year,
            "poster_url": item.poster_url,
            "external_api_id": item.external_api_id,
            "external_api_source": item.external_api_source,
            "genres": item.genres,
            "authors": item.authors,
            "director": item.director,
            "actors": item.actors,
            "page_count": item.page_count,
            "created_at": item.created_at,
            **rating_info
        }
        result.append(item_dict)
    
    return result


# 🎯 Gelişmiş Filtreleme
@router.get("/filter", response_model=list[schemas.ItemOut])
def filter_items(
    item_type: str = Query(None, description="'book' veya 'movie'"),
    year_from: int = Query(None, ge=1900),
    year_to: int = Query(None, le=2099),
    rating_min: float = Query(None, ge=0, le=10),
    genre: str = Query(None, description="Tür filtresi"),
    db: Session = Depends(get_db)
):
    """Gelişmiş filtreleme ile içerik ara"""
    query = db.query(models.Item)
    
    if item_type:
        query = query.filter(models.Item.item_type == item_type)
    if year_from:
        query = query.filter(models.Item.year >= year_from)
    if year_to:
        query = query.filter(models.Item.year <= year_to)
    if rating_min:
        query = query.filter(models.Item.external_rating >= rating_min)
    
    items = query.limit(50).all()
    
    result = []
    for item in items:
        rating_info = calculate_hybrid_rating(item.item_id, item, db)
        item_dict = {
            "item_id": item.item_id,
            "title": item.title,
            "description": item.description,
            "item_type": item.item_type,
            "year": item.year,
            "poster_url": item.poster_url,
            "external_api_id": item.external_api_id,
            "external_api_source": item.external_api_source,
            "genres": item.genres,
            "authors": item.authors,
            "director": item.director,
            "actors": item.actors,
            "page_count": item.page_count,
            "created_at": item.created_at,
            **rating_info
        }
        result.append(item_dict)
    
    return result


# ============================================
# 2️⃣ CRUD ROUTES (Dinamik route'lar SONDA)
# ============================================

# 📋 Tüm içerikleri listele
@router.get("/", response_model=list[schemas.ItemOut])
def get_items(db: Session = Depends(get_db), limit: int = 20):
    """Tüm içerikleri listele"""
    items = db.query(models.Item).limit(limit).all()
    
    result = []
    for item in items:
        rating_info = calculate_hybrid_rating(item.item_id, item, db)
        item_dict = {
            "item_id": item.item_id,
            "title": item.title,
            "description": item.description,
            "item_type": item.item_type,
            "year": item.year,
            "poster_url": item.poster_url,
            "external_api_id": item.external_api_id,
            "external_api_source": item.external_api_source,
            "genres": item.genres,
            "authors": item.authors,
            "director": item.director,
            "actors": item.actors,
            "page_count": item.page_count,
            "created_at": item.created_at,
            **rating_info
        }
        result.append(item_dict)
    
    return result


# ➕ Yeni içerik ekle
@router.post("/", response_model=schemas.ItemOut)
def create_item(item: schemas.ItemCreate, db: Session = Depends(get_db)):
    """Yeni içerik ekle"""
    new_item = models.Item(**item.dict())
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item


# 📊 Tekil içeriğin puan bilgisini getir
@router.get("/{item_id}/rating")
def get_item_rating(item_id: int, db: Session = Depends(get_db)):
    """İçeriğin puan bilgisini getir"""
    item = db.query(models.Item).filter(models.Item.item_id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="İçerik bulunamadı")
    
    rating_info = calculate_hybrid_rating(item.item_id, item, db)
    return rating_info


# 🔍 Tekil içeriği id ile getir
@router.get("/{item_id}", response_model=schemas.ItemOut)
def get_item(item_id: int, db: Session = Depends(get_db)):
    """Tekil içerik detayları"""
    item = db.query(models.Item).filter(models.Item.item_id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="İçerik bulunamadı")
    
    rating_info = calculate_hybrid_rating(item.item_id, item, db)
    item_dict = {
        "item_id": item.item_id,
        "title": item.title,
        "description": item.description,
        "item_type": item.item_type,
        "year": item.year,
        "poster_url": item.poster_url,
        "external_api_id": item.external_api_id,
        "external_api_source": item.external_api_source,
        "genres": item.genres,
        "authors": item.authors,
        "director": item.director,
        "actors": item.actors,
        "page_count": item.page_count,
        "created_at": item.created_at,
        **rating_info
    }
    return item_dict


# ✏️ İçerik güncelle
@router.put("/{item_id}", response_model=schemas.ItemOut)
def update_item(item_id: int, item_update: schemas.ItemCreate, db: Session = Depends(get_db)):
    """İçerik bilgilerini güncelle"""
    item = db.query(models.Item).filter(models.Item.item_id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="İçerik bulunamadı")
    
    update_data = item_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)
    
    db.commit()
    db.refresh(item)
    return item


# ❌ İçerik sil
@router.delete("/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    """İçerik sil"""
    item = db.query(models.Item).filter(models.Item.item_id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="İçerik bulunamadı")
    
    db.delete(item)
    db.commit()
    return {"message": "İçerik başarıyla silindi"}


# ⭐ Favorilere ekle
@router.post("/{item_id}/favorite")
def add_to_favorite(item_id: int, user_id: int = Query(...)):
    """Favorilere ekle"""
    return {"message": "Favorilere eklendi", "item_id": item_id}


# 📝 Listeye ekle
@router.post("/{item_id}/add-to-list")
def add_to_list(item_id: int, list_id: int = Query(...)):
    """Listeye ekle"""
    return {"message": "Listeye eklendi", "item_id": item_id}


# ============================================
# DETAIL PAGE ENDPOINTS
# ============================================

# 📖 İçerik detayını getir
@router.get("/{item_id}", response_model=schemas.ItemOut)
def get_item_detail(item_id: int, db: Session = Depends(get_db)):
    """İçeriğin detaylı bilgisini getir"""
    item = db.query(models.Item).filter(models.Item.item_id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="İçerik bulunamadı")
    
    rating_info = calculate_hybrid_rating(item_id, item, db)
    
    item_dict = {
        "item_id": item.item_id,
        "title": item.title,
        "item_type": item.item_type,
        "description": item.description,
        "poster_url": item.poster_url,
        "year": item.year,
        "authors": item.authors,
        "director": item.director,
        "actors": item.actors,
        "page_count": item.page_count,
        "genres": item.genres,
        "created_at": item.created_at,
        **rating_info
    }
    return item_dict


# 💬 İçeriğin tüm yorumlarını getir
@router.get("/{item_id}/comments", response_model=list[schemas.ReviewOut])
def get_item_comments(item_id: int, db: Session = Depends(get_db)):
    """İçeriğin tüm yorumlarını getir"""
    item = db.query(models.Item).filter(models.Item.item_id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="İçerik bulunamadı")
    
    comments = db.query(models.Review).filter(
        models.Review.item_id == item_id
    ).all()
    
    return comments


# ➕ Yeni yorum ekle
@router.post("/{item_id}/comments", response_model=schemas.ReviewOut)
def add_comment(item_id: int, review: schemas.ReviewCreate, db: Session = Depends(get_db)):
    """İçeriğe yeni yorum ekle"""
    # Check if item exists
    item = db.query(models.Item).filter(models.Item.item_id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="İçerik bulunamadı")
    
    # Create new review
    new_review = models.Review(
        item_id=item_id,
        user_id=review.user_id,
        review_text=review.review_text,
        rating=review.rating
    )
    
    db.add(new_review)
    db.commit()
    db.refresh(new_review)
    
    return new_review


# ============================================
# API ITEMS ENDPOINTS (Harici API kaynakları için)
# ============================================

@router.get("/api/comments/{source_id}")
def get_api_comments(source_id: str, db: Session = Depends(get_db)):
    """
    API items (TMDB/Google Books) için yorumlarını getir
    source_id: "tmdb_550" veya "google_books_abc123" format
    """
    try:
        # source_id'yi parse et: "tmdb_550" → ("tmdb", "550")
        parts = source_id.rsplit('_', 1)
        if len(parts) != 2:
            return {"success": False, "comments": [], "error": "Geçersiz source_id format"}
        
        source_type, api_id = parts
        comments = []
        
        # TMDB film yorumlarını çek
        if source_type == "tmdb":
            comments = get_tmdb_reviews(api_id)
        
        # Google Books kitap yorumlarını çek
        elif source_type == "google_books":
            comments = get_google_books_reviews(api_id)
        
        # OpenLibrary (henüz impl yok)
        elif source_type == "openlib":
            return {
                "success": True,
                "comments": [],
                "message": "OpenLibrary API henüz yorum desteği yok"
            }
        
        else:
            return {
                "success": False,
                "comments": [],
                "error": f"Bilinmeyen kaynak: {source_type}"
            }
        
        return {
            "success": True,
            "comments": comments,
            "source_id": source_id,
            "total": len(comments)
        }
    
    except Exception as e:
        print(f"Error fetching API comments: {e}")
        return {
            "success": False,
            "comments": [],
            "error": str(e)
        }


@router.post("/api/comments/{source_id}")
def add_api_comment(source_id: str, comment: dict, db: Session = Depends(get_db)):
    """
    API items için yorum ekle (TMDB/Google Books)
    """
    try:
        # API item yorumları için mock response döndür
        # Gerçek kullanımda bu veritabanına kaydedilecek
        return {
            "success": True,
            "message": "Yorum başarıyla eklendi",
            "source_id": source_id,
            "user_id": comment.get("user_id"),
            "rating": comment.get("rating"),
            "review_text": comment.get("review_text")
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# 📊 RATING: Kullanıcı puanını kaydet
@router.post("/{item_id}/rate")
def rate_item(item_id: int, rating_data: dict, db: Session = Depends(get_db)):
    """
    Kullanıcı tarafından bir item'e puan ver (1-10)
    Varsa update, yoksa create et
    """
    try:
        # Girdileri kontrol et
        if "rating" not in rating_data:
            raise HTTPException(status_code=400, detail="Rating alanı gerekli")
        
        rating = rating_data.get("rating")
        if not isinstance(rating, (int, float)) or rating < 1 or rating > 10:
            raise HTTPException(status_code=400, detail="Puan 1-10 arasında olmalı")
        
        user_id = rating_data.get("user_id")
        if not user_id:
            raise HTTPException(status_code=400, detail="Kullanıcı ID gerekli")
        
        # Item var mı?
        item = db.query(models.Item).filter(models.Item.item_id == item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Item bulunamadı")
        
        # Kullanıcının bu item için zaten review'ı var mı?
        existing_review = db.query(models.Review).filter(
            models.Review.item_id == item_id,
            models.Review.user_id == user_id
        ).first()
        
        if existing_review:
            # Varsa güncelle
            existing_review.rating = rating
            existing_review.review_text = rating_data.get("review_text", "")
            db.commit()
            db.refresh(existing_review)
            
            return {
                "success": True,
                "message": "Puan güncellendi",
                "review_id": existing_review.review_id,
                "rating": existing_review.rating,
                "created_at": existing_review.created_at
            }
        else:
            # Yoksa yarat
            new_review = models.Review(
                user_id=user_id,
                item_id=item_id,
                rating=rating,
                review_text=rating_data.get("review_text", "")
            )
            db.add(new_review)
            db.commit()
            db.refresh(new_review)
            
            return {
                "success": True,
                "message": "Puan kaydedildi",
                "review_id": new_review.review_id,
                "rating": new_review.rating,
                "created_at": new_review.created_at
            }
    
    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Puan kaydı hatası: {str(e)}")