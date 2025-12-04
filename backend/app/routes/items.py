from fastapi import APIRouter, Depends, HTTPException, Query, Body
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
    # User reviews'ten rating hesapla (reviews tablosundan)
    rating_query = text("""
        SELECT AVG(rating) as avg_rating, COUNT(*) as total_ratings
        FROM reviews
        WHERE item_id = :item_id AND rating IS NOT NULL
    """)
    rating_result = db.execute(rating_query, {"item_id": item_id}).first()
    
    user_rating_from_reviews = rating_result[0] or 0
    review_count = rating_result[1] or 0
    
    # User ratings'ten rating hesapla (ratings tablosundan)
    ratings_query = text("""
        SELECT AVG(score) as avg_score, COUNT(*) as total_ratings
        FROM ratings
        WHERE item_id = :item_id
    """)
    ratings_result = db.execute(ratings_query, {"item_id": item_id}).first()
    
    user_rating_from_ratings = ratings_result[0] or 0
    ratings_count = ratings_result[1] or 0
    
    # Combine both ratings
    total_rating_count = review_count + ratings_count
    
    if total_rating_count > 0:
        # Average of all ratings (both reviews and ratings table)
        user_rating = round((user_rating_from_reviews * review_count + user_rating_from_ratings * ratings_count) / total_rating_count, 1)
    else:
        user_rating = 0
    
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
        "review_count": total_rating_count,  # Total ratings from both reviews and ratings table
        "popularity": total_rating_count  # Popularity = total rating count
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
    """En yüksek puanlı içerikleri getir (combined_rating'e göre sıralanmış)"""
    # Tüm items'ı getir ve combined rating hesapla
    all_items = db.query(models.Item).all()
    
    # Her item için combined rating hesapla
    items_with_ratings = []
    for item in all_items:
        rating_info = calculate_hybrid_rating(item.item_id, item, db)
        combined = rating_info.get('combined_rating', 0)
        items_with_ratings.append((item, rating_info, combined))
    
    # Combined rating'e göre sırala ve top N'i al
    items_with_ratings.sort(key=lambda x: x[2], reverse=True)
    top_items = items_with_ratings[:limit]
    
    result = []
    for item, rating_info, _ in top_items:
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


# 👥 En Popülerler (En çok review alanlar + rating)
@router.get("/featured/popular", response_model=list[schemas.ItemOut])
def get_popular(limit: int = Query(6, ge=1, le=50), db: Session = Depends(get_db)):
    """En popüler içerikleri getir (review count'a göre, sonra rating'e göre sıralanmış)"""
    # Tüm items'ı getir
    all_items = db.query(models.Item).all()
    
    # Her item için combined rating ve review count hesapla
    items_with_scores = []
    for item in all_items:
        rating_info = calculate_hybrid_rating(item.item_id, item, db)
        review_count = rating_info.get('review_count', 0)
        combined_rating = rating_info.get('combined_rating', 0)
        
        # Popularity skoru: review_count * combined_rating (ikisini de dikkate al)
        # Bu şekilde hem popülarite hem kalite önemli
        if review_count > 0:
            popularity_score = (review_count * 2) + combined_rating  # Review count'ı daha ağırlıklandır
        else:
            popularity_score = combined_rating  # Review yok ise sadece rating'e bak
        
        items_with_scores.append((item, rating_info, popularity_score, review_count))
    
    # Popularity score'a göre sırala ve top N'i al
    items_with_scores.sort(key=lambda x: (x[2], x[3]), reverse=True)  # Score ve review count'a göre
    top_items = items_with_scores[:limit]
    
    result = []
    for item, rating_info, _, _ in top_items:
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
# DETAIL PAGE ENDPOINTS (DUPLICATE REMOVED - Using first definition above)
# ============================================


# 💬 İçeriğin tüm yorumlarını getir
@router.get("/{item_id}/comments", response_model=list[schemas.ReviewOut])
def get_item_comments(item_id: int, db: Session = Depends(get_db)):
    """İçeriğin tüm yorumlarını getir"""
    item = db.query(models.Item).filter(models.Item.item_id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="İçerik bulunamadı")
    
    reviews = db.query(models.Review).filter(
        models.Review.item_id == item_id
    ).all()
    
    # Add username and avatar to each review
    result = []
    for review in reviews:
        user = db.query(models.User).filter(models.User.user_id == review.user_id).first()
        review_dict = {
            "review_id": review.review_id,
            "user_id": review.user_id,
            "username": user.username if user else f"User {review.user_id}",
            "avatar_url": user.avatar_url if user else None,
            "item_id": review.item_id,
            "review_text": review.review_text,
            "rating": review.rating,
            "created_at": review.created_at
        }
        result.append(schemas.ReviewOut(**review_dict))
    
    return result


# ⭐ İçeriğin tüm puanlarını getir
@router.get("/{item_id}/ratings", response_model=list[schemas.RatingOut])
def get_item_ratings(item_id: int, db: Session = Depends(get_db)):
    """İçeriğin tüm puanlarını getir (ratings tablosundan)"""
    item = db.query(models.Item).filter(models.Item.item_id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="İçerik bulunamadı")
    
    ratings = db.query(models.Rating).filter(
        models.Rating.item_id == item_id
    ).order_by(models.Rating.created_at.desc()).all()
    
    # Add username and avatar to each rating
    result = []
    for rating in ratings:
        user = db.query(models.User).filter(models.User.user_id == rating.user_id).first()
        result.append(
            schemas.RatingOut(
                rating_id=rating.rating_id,
                user_id=rating.user_id,
                username=user.username if user else f"User {rating.user_id}",
                avatar_url=user.avatar_url if user else None,
                item_id=rating.item_id,
                score=rating.score,
                created_at=rating.created_at
            )
        )
    
    return result


# 🗑️ Puanı sil
@router.delete("/rating/{rating_id}")
def delete_rating(rating_id: int, db: Session = Depends(get_db)):
    """Puanı sil (sadece kendi puanını silebilir)"""
    try:
        rating = db.query(models.Rating).filter(models.Rating.rating_id == rating_id).first()
        if not rating:
            raise HTTPException(status_code=404, detail="Puan bulunamadı")
        
        db.delete(rating)
        db.commit()
        print(f"✅ Puan {rating_id} silindi")
        return {"message": "✅ Puan başarıyla silindi", "rating_id": rating_id}
    
    except Exception as e:
        db.rollback()
        print(f"❌ Puan silme hatası: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Puan silme hatası: {str(e)}")


# ➕ Yeni yorum ekle
@router.post("/{item_id}/comments", response_model=schemas.ReviewOut)
def add_comment(item_id: int, review: schemas.ReviewCreate, db: Session = Depends(get_db)):
    """İçeriğe yeni yorum ekle"""
    # Check if item exists
    item = db.query(models.Item).filter(models.Item.item_id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="İçerik bulunamadı")
    
    # Find the next available review_id (reuse deleted IDs)
    # Get all existing IDs
    existing_ids_query = db.query(models.Review.review_id).all()
    existing_ids = {row[0] for row in existing_ids_query}
    
    # Find the first available ID (starting from 1)
    next_id = 1
    while next_id in existing_ids:
        next_id += 1
    
    # Create new review with assigned ID
    new_review = models.Review(
        review_id=next_id,
        item_id=item_id,
        user_id=review.user_id,
        review_text=review.review_text,
        rating=review.rating
    )
    
    db.add(new_review)
    db.flush()  # Get the ID before commit
    
    # Activity kaydı oluştur
    activity = models.Activity(
        user_id=review.user_id,
        activity_type="review",
        item_id=item_id,
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


# ============================================
# API ITEMS ENDPOINTS (Harici API kaynakları için)
# ============================================

@router.get("/api/comments/{source_id}")
def get_api_comments(source_id: str, db: Session = Depends(get_db)):
    """
    API items (TMDB/Google Books) için yorumlarını getir
    source_id: "tmdb_550" veya "google_books_abc123" format
    
    1. Veritabanında source_id ile kaydedilen yorumları getir
    2. Eğer item database'e import edildiyse, o item'ın yorumlarını da getir
    3. Dış API'den çek
    """
    try:
        all_comments_list = []
        
        # 1. Veritabanından source_id ile yorumları getir
        db_comments = db.query(models.Review).filter(
            models.Review.source_id == source_id
        ).order_by(models.Review.created_at.desc()).all()
        
        for review in db_comments:
            user = db.query(models.User).filter(models.User.user_id == review.user_id).first()
            all_comments_list.append({
                "review_id": review.review_id,
                "user_id": review.user_id,
                "username": user.username if user else f"User {review.user_id}",
                "avatar_url": user.avatar_url if user else None,
                "review_text": review.review_text,
                "rating": review.rating,
                "created_at": review.created_at.isoformat() if review.created_at else None,
                "source": "user_comment"
            })
        
        # 2. Eğer bu item database'e import edildiyse, o item'ın yorumlarını da getir
        # source_id'den item'ı bulalım
        imported_item = db.query(models.Item).filter(
            models.Item.external_api_id == source_id
        ).first()
        
        if imported_item:
            # Bu item'ın tüm yorumlarını getir (ratings dahil)
            item_reviews = db.query(models.Review).filter(
                models.Review.item_id == imported_item.item_id
            ).order_by(models.Review.created_at.desc()).all()
            
            for review in item_reviews:
                user = db.query(models.User).filter(models.User.user_id == review.user_id).first()
                all_comments_list.append({
                    "review_id": review.review_id,
                    "user_id": review.user_id,
                    "username": user.username if user else f"User {review.user_id}",
                    "avatar_url": user.avatar_url if user else None,
                    "review_text": review.review_text,
                    "rating": review.rating,
                    "created_at": review.created_at.isoformat() if review.created_at else None,
                    "source": "user_rating"
                })
        
        # 3. source_id'yi parse et: "tmdb_550" → ("tmdb", "550")
        parts = source_id.rsplit('_', 1)
        if len(parts) == 2:
            source_type, api_id = parts
            api_comments = []
            
            # TMDB film yorumlarını çek
            if source_type == "tmdb":
                api_comments = get_tmdb_reviews(api_id)
            
            # Google Books kitap yorumlarını çek
            elif source_type == "google_books":
                api_comments = get_google_books_reviews(api_id)
            
            # API yorumlarını ekle
            all_comments_list.extend(api_comments)
        
        # Duplikatları kaldır (aynı user ve text olanlar)
        seen = set()
        unique_comments = []
        for comment in all_comments_list:
            key = (comment.get("user_id"), comment.get("review_text")[:50] if comment.get("review_text") else "")
            if key not in seen:
                seen.add(key)
                unique_comments.append(comment)
        
        return {
            "success": True,
            "comments": unique_comments,
            "source_id": source_id,
            "total": len(unique_comments)
        }
    
    except Exception as e:
        print(f"Error fetching API comments: {e}")
        return {
            "success": False,
            "comments": [],
            "error": str(e)
        }


@router.post("/api/comments/{source_id}")
def add_api_comment(source_id: str, comment: dict = Body(...), db: Session = Depends(get_db)):
    """
    API items için yorum ekle (TMDB/Google Books)
    Yorum reviews table'ına kaydedilir ve item_id olacak (DB'ye otomatik kaydedilir)
    """
    try:
        print(f"📝 API Comment POST: {source_id}, Data: {comment}")
        
        user_id = comment.get("user_id")
        review_text = comment.get("review_text")
        rating = comment.get("rating")
        title = comment.get("title", "Unknown")
        item_type = comment.get("item_type", "movie")
        poster_url = comment.get("poster_url", "")
        year = comment.get("year")
        description = comment.get("description", "")
        
        if not user_id:
            raise HTTPException(status_code=400, detail="user_id gerekli")
        if not review_text:
            raise HTTPException(status_code=400, detail="review_text gerekli")
        
        # API item'ı DB'ye kaydet (varsa skip et)
        existing_item = db.query(models.Item).filter(
            models.Item.external_api_id == source_id
        ).first()
        
        if not existing_item:
            new_item = models.Item(
                title=title,
                item_type=item_type,
                year=year,
                description=description,
                poster_url=poster_url,
                external_api_id=source_id,
                external_api_source="external",
                external_rating=0
            )
            db.add(new_item)
            db.flush()
            item_id = new_item.item_id
        else:
            item_id = existing_item.item_id
        
        # Find the next available review_id (reuse deleted IDs)
        existing_ids_query = db.query(models.Review.review_id).all()
        existing_ids = {row[0] for row in existing_ids_query}
        
        # Find the first available ID (starting from 1)
        next_id = 1
        while next_id in existing_ids:
            next_id += 1
        
        # Review kaydı oluştur
        new_review = models.Review(
            review_id=next_id,
            user_id=user_id,
            item_id=item_id,  # ← Artık item_id var!
            source_id=source_id,  # Referans için tut
            review_text=review_text,
            rating=rating if rating and 1 <= rating <= 10 else None
        )
        
        db.add(new_review)
        db.flush()
        
        # Activity kaydı oluştur - item_id ile
        activity = models.Activity(
            user_id=user_id,
            activity_type="review",
            item_id=item_id,  # ← item_id'yi Activity'ye yaz
            review_id=new_review.review_id
        )
        db.add(activity)
        db.commit()
        db.refresh(new_review)
        
        return {
            "success": True,
            "message": "Yorum başarıyla eklendi",
            "source_id": source_id,
            "review_id": new_review.review_id,
            "item_id": item_id,
            "user_id": user_id,
            "rating": rating
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


# 📊 RATING: Kullanıcı puanını kaydet
@router.post("/{item_id}/rate")
def rate_item(item_id: int, rating_data: dict, db: Session = Depends(get_db)):
    """
    Kullanıcı tarafından bir item'e puan ver (1-10)
    Ratings tablosuna kaydedilir
    Varsa update, yoksa create et
    Gap-filling: Deleted rating IDs are reused
    """
    try:
        print(f"\n🔴 ====== RATING REQUEST BAŞLADI ======")
        print(f"📍 item_id: {item_id}")
        print(f"📍 rating_data: {rating_data}")
        
        # Girdileri kontrol et
        if "rating" not in rating_data:
            print(f"❌ 'rating' alanı bulunamadı")
            raise HTTPException(status_code=400, detail="Rating alanı gerekli")
        
        rating = rating_data.get("rating")
        print(f"📊 rating value: {rating}, type: {type(rating)}")
        
        if not isinstance(rating, (int, float)) or rating < 1 or rating > 10:
            print(f"❌ Rating validation failed: {rating}")
            raise HTTPException(status_code=400, detail="Puan 1-10 arasında olmalı")
        
        user_id = rating_data.get("user_id")
        print(f"👤 user_id: {user_id}")
        
        if not user_id:
            print(f"❌ user_id bulunamadı")
            raise HTTPException(status_code=400, detail="Kullanıcı ID gerekli")
        
        # Item var mı?
        item = db.query(models.Item).filter(models.Item.item_id == item_id).first()
        print(f"🔍 Item found: {item is not None}")
        
        if not item:
            print(f"❌ Item {item_id} not found")
            raise HTTPException(status_code=404, detail="Item bulunamadı")
        
        # Kullanıcının bu item için zaten puanı var mı?
        existing_rating = db.query(models.Rating).filter(
            models.Rating.item_id == item_id,
            models.Rating.user_id == user_id
        ).first()
        
        print(f"🔍 Existing rating found: {existing_rating is not None}")
        
        if existing_rating:
            # Varsa güncelle
            print(f"📝 Updating existing rating {existing_rating.rating_id}")
            existing_rating.score = rating
            db.commit()
            db.refresh(existing_rating)
            
            print(f"✅ Rating updated: rating_id={existing_rating.rating_id}, score={existing_rating.score}")
            return {
                "success": True,
                "message": "Puan güncellendi",
                "rating_id": existing_rating.rating_id,
                "rating": existing_rating.score,
                "created_at": existing_rating.created_at
            }
        else:
            # Yoksa yarat - gap-filling with next available ID
            print(f"➕ Creating new rating with gap-filling")
            
            # Get all existing rating IDs
            existing_ids_query = db.query(models.Rating.rating_id).all()
            existing_ids = {row[0] for row in existing_ids_query}
            print(f"🔍 Existing rating IDs: {sorted(existing_ids)}")
            
            # Find the first available ID (starting from 1)
            next_id = 1
            while next_id in existing_ids:
                next_id += 1
            
            print(f"✨ Next available rating_id: {next_id}")
            
            new_rating = models.Rating(
                rating_id=next_id,
                user_id=user_id,
                item_id=item_id,
                score=rating
            )
            db.add(new_rating)
            db.flush()  # Get the ID before commit
            
            # Activity kaydı oluştur (yeni rating oluşturulduğunda)
            activity = models.Activity(
                user_id=user_id,
                activity_type="rating",
                item_id=item_id
            )
            db.add(activity)
            db.commit()
            db.refresh(new_rating)
            
            print(f"✅ Rating created: rating_id={new_rating.rating_id}, score={new_rating.score}")
            return {
                "success": True,
                "message": "Puan kaydedildi",
                "rating_id": new_rating.rating_id,
                "rating": new_rating.score,
                "created_at": new_rating.created_at
            }
    
    except HTTPException as he:
        print(f"❌ HTTPException: {he.detail}")
        raise he
    except Exception as e:
        db.rollback()
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Puan kaydı hatası: {str(e)}")


# ============ KÜTÜPHANE: İçeriği listeye ekle/çıkar ============
@router.post("/{item_id}/library")
def add_to_library(item_id: int, data: dict = Body(...), db: Session = Depends(get_db)):
    """
    Kullanıcının kütüphanesine içerik ekle/çıkar
    status: 'read', 'toread', 'watched', 'towatch'
    action: 'add' veya 'remove'
    
    NOT: Bir user aynı item'ı sadece BİR status'ta tutabilir.
    Eğer yeni status ile eklenirse, eski status silinip yenisi eklenir.
    """
    try:
        user_id = data.get("user_id")
        status = data.get("status")
        action = data.get("action", "add")  # 'add' or 'remove'
        
        if not user_id or not status:
            raise HTTPException(status_code=400, detail="user_id ve status gerekli")
        
        if status not in ['read', 'toread', 'watched', 'towatch']:
            raise HTTPException(status_code=400, detail="Geçersiz status")
        
        # Item var mı?
        item = db.query(models.Item).filter(models.Item.item_id == item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="İçerik bulunamadı")
        
        if action == "add":
            # Önce bu user/item için başka status'ta kayıt var mı kontrol et
            existing_entry = db.query(models.UserLibrary).filter(
                models.UserLibrary.user_id == user_id,
                models.UserLibrary.item_id == item_id
            ).first()
            
            if existing_entry:
                # Varsa, aynı library_id ile status'unu güncelle (ID değişmez!)
                if existing_entry.status == status:
                    return {
                        "success": True,
                        "message": "Bu status zaten kütüphanede var",
                        "item_id": item_id,
                        "status": status,
                        "library_id": existing_entry.library_id,
                        "action": "add"
                    }
                
                # Farklı status ise, GÜNCELLE (DELETE+INSERT yerine)
                existing_entry.status = status
                db.commit()
                db.refresh(existing_entry)
                
                return {
                    "success": True,
                    "message": f"Status '{status}' olarak güncellendi (aynı ID ile)",
                    "item_id": item_id,
                    "status": status,
                    "library_id": existing_entry.library_id,
                    "action": action
                }
            else:
                # Yeni kayıt ekle
                library_entry = models.UserLibrary(
                    user_id=user_id,
                    item_id=item_id,
                    status=status
                )
                db.add(library_entry)
                db.commit()
                db.refresh(library_entry)
                
                return {
                    "success": True,
                    "message": f"Status '{status}' olarak eklendi (yeni ID: {library_entry.library_id})",
                    "item_id": item_id,
                    "status": status,
                    "library_id": library_entry.library_id,
                    "action": action
                }
        
        elif action == "remove":
            deleted = db.query(models.UserLibrary).filter(
                models.UserLibrary.user_id == user_id,
                models.UserLibrary.item_id == item_id,
                models.UserLibrary.status == status
            ).delete()
            db.commit()
            
            return {
                "success": True,
                "message": f"İçerik kütüphaneden kaldırıldı ({deleted} kayıt)",
                "item_id": item_id,
                "status": status,
                "action": action,
                "deleted_count": deleted
            }
    
    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# ============ KÜTÜPHANEYİ GETIR ============
@router.get("/library/{user_id}")
def get_user_library(user_id: int, status: str = Query(None), db: Session = Depends(get_db)):
    """
    Kullanıcının kütüphanesini getir
    status parametresi opsiyonel: 'read', 'toread', 'watched', 'towatch'
    """
    try:
        query = db.query(models.UserLibrary).filter(
            models.UserLibrary.user_id == user_id
        )
        
        if status:
            query = query.filter(models.UserLibrary.status == status)
        
        library_entries = query.all()
        
        items = []
        for entry in library_entries:
            item = db.query(models.Item).filter(models.Item.item_id == entry.item_id).first()
            if item:
                items.append({
                    "library_id": entry.library_id,
                    "item_id": entry.item_id,
                    "status": entry.status,
                    "title": item.title,
                    "item_type": item.item_type,
                    "poster_url": item.poster_url,
                    "added_at": entry.added_at
                })
        
        return {
            "success": True,
            "user_id": user_id,
            "status_filter": status,
            "items": items,
            "total": len(items)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ ÖZEL LİSTE: OLUŞTUR ============
@router.post("/custom-lists")
def create_custom_list(data: dict = Body(...), db: Session = Depends(get_db)):
    """
    Kullanıcının listesi oluştur
    """
    try:
        user_id = data.get("user_id")
        name = data.get("name")
        description = data.get("description", "")
        is_public = data.get("is_public", 0)
        
        if not user_id or not name:
            raise HTTPException(status_code=400, detail="user_id ve name gerekli")
        
        new_list = models.CustomList(
            user_id=user_id,
            name=name,
            description=description,
            is_public=is_public
        )
        db.add(new_list)
        db.flush()  # Get the ID before commit
        
        # Activity kaydı oluştur
        activity = models.Activity(
            user_id=user_id,
            activity_type="list_add",
            list_id=new_list.list_id
        )
        db.add(activity)
        db.commit()
        db.refresh(new_list)
        
        return {
            "success": True,
            "message": "Liste oluşturuldu",
            "list_id": new_list.list_id,
            "name": new_list.name
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# ============ ÖZEL LİSTE: GETIR ============
@router.get("/custom-lists/{user_id}")
def get_custom_lists(user_id: int, db: Session = Depends(get_db)):
    """
    Kullanıcının tüm özel listelerini getir
    """
    try:
        lists = db.query(models.CustomList).filter(
            models.CustomList.user_id == user_id
        ).all()
        
        custom_lists = []
        for lst in lists:
            items = db.query(models.ListItem).filter(
                models.ListItem.list_id == lst.list_id
            ).count()
            
            custom_lists.append({
                "list_id": lst.list_id,
                "name": lst.name,
                "description": lst.description,
                "is_public": lst.is_public,
                "item_count": items,
                "created_at": lst.created_at,
                "updated_at": lst.updated_at
            })
        
        return {
            "success": True,
            "user_id": user_id,
            "lists": custom_lists,
            "total": len(custom_lists)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ ÖZEL LİSTE: İTEM EKLE/ÇIKAR ============
@router.post("/custom-lists/{list_id}/items")
def add_to_custom_list(list_id: int, data: dict = Body(...), db: Session = Depends(get_db)):
    """
    Özel listeye item ekle/çıkar
    item_id: DB itemi için
    source_id: API itemi için (tmdb_123, google_books_456, vb.)
    """
    try:
        item_id = data.get("item_id")
        source_id = data.get("source_id")
        action = data.get("action", "add")  # 'add' or 'remove'
        position = data.get("position", 0)  # Sıralama
        
        # List var mı?
        custom_list = db.query(models.CustomList).filter(
            models.CustomList.list_id == list_id
        ).first()
        if not custom_list:
            raise HTTPException(status_code=404, detail="Liste bulunamadı")
        
        # item_id veya source_id gerekli
        if not item_id and not source_id:
            raise HTTPException(status_code=400, detail="item_id veya source_id gerekli")
        
        # Eğer source_id varsa, API itemini DB'ye kaydet ve item_id al
        if source_id and not item_id:
            # Check if API item already exists
            existing_item = db.query(models.Item).filter(
                models.Item.external_api_id == source_id
            ).first()
            
            if not existing_item:
                # API item metadata'sını al ve DB'ye kaydet
                title = data.get("title", "Unknown")
                item_type = data.get("item_type", "movie")
                poster_url = data.get("poster_url", "")
                year = data.get("year")
                description = data.get("description", "")
                
                new_item = models.Item(
                    title=title,
                    item_type=item_type,
                    year=year,
                    description=description,
                    poster_url=poster_url,
                    external_api_id=source_id,
                    external_api_source="external",
                    external_rating=0
                )
                db.add(new_item)
                db.flush()
                item_id = new_item.item_id
            else:
                item_id = existing_item.item_id
        
        # DB item ise kontrol et
        if item_id:
            item = db.query(models.Item).filter(models.Item.item_id == item_id).first()
            if not item:
                raise HTTPException(status_code=404, detail="İçerik bulunamadı")
        
        if action == "add":
            # Duplicate kontrol
            existing = db.query(models.ListItem).filter(
                models.ListItem.list_id == list_id,
                models.ListItem.item_id == item_id
            ).first()
            
            if existing:
                return {
                    "success": True,
                    "message": "Bu item zaten listede var",
                    "list_id": list_id,
                    "item_id": item_id,
                    "source_id": source_id,
                    "action": action
                }
            
            list_item = models.ListItem(
                list_id=list_id,
                item_id=item_id,
                position=position
            )
            db.add(list_item)
            db.flush()  # Get the ID before commit
            
            # Activity kaydı oluştur (item listeye eklendiğinde)
            activity = models.Activity(
                user_id=custom_list.user_id,
                activity_type="list_add",
                list_id=list_id,
                item_id=item_id
            )
            db.add(activity)
            db.commit()
        
        elif action == "remove":
            db.query(models.ListItem).filter(
                models.ListItem.list_id == list_id,
                models.ListItem.item_id == item_id
            ).delete()
            db.commit()
        
        return {
            "success": True,
            "message": f"Item {action}landı",
            "list_id": list_id,
            "item_id": item_id,
            "source_id": source_id,
            "action": action
        }
    
    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# ============ API İÇERİK: KÜTÜPHANEYE EKLE ============
@router.post("/api/library/{source_id}")
def add_api_item_to_library(source_id: str, data: dict = Body(...), db: Session = Depends(get_db)):
    """
    API kaynağından gelen içeriği (TMDB/Google Books) kütüphaneye ekle
    source_id: 'tmdb_123', 'google_books_abc123', vb.
    
    NOT: Bir user aynı API item'ı sadece BİR status'ta tutabilir.
    Eğer yeni status ile eklenirse, eski status silinip yenisi eklenir.
    """
    try:
        user_id = data.get("user_id")
        status = data.get("status")  # 'read', 'toread', 'watched', 'towatch'
        action = data.get("action", "add")  # 'add' or 'remove'
        title = data.get("title", "")
        item_type = data.get("item_type", "")
        poster_url = data.get("poster_url", "")
        year = data.get("year")
        description = data.get("description", "")
        
        if not user_id or not status or not source_id:
            raise HTTPException(status_code=400, detail="user_id, status ve source_id gerekli")
        
        # Ensure title is not empty - if empty, try to fetch from TMDB/API
        if not title or title.strip() == "":
            # Try to get from existing item or fetch from external API
            existing_item_check = db.query(models.Item).filter(
                models.Item.external_api_id == source_id
            ).first()
            if existing_item_check and existing_item_check.title:
                title = existing_item_check.title
            else:
                # Fallback: If still empty, set to Unknown with source_id
                title = f"Unknown ({source_id})"
        
        # Status validation
        valid_statuses = ['read', 'toread', 'watched', 'towatch']
        if status not in valid_statuses:
            raise HTTPException(status_code=400, detail=f"Status {valid_statuses} içinden olmalı")
        
        if action == "add":
            # Check if API item already exists in items table
            existing_item = db.query(models.Item).filter(
                models.Item.external_api_id == source_id
            ).first()
            
            # Ensure title is not empty
            if not title or title.strip() == "":
                title = "Unknown"
            
            # If not exists, create it automatically
            if not existing_item:
                new_item = models.Item(
                    title=title,
                    item_type=item_type,
                    year=year,
                    description=description,
                    poster_url=poster_url,
                    external_api_id=source_id,
                    external_api_source="external",  # Marking as external/API source
                    external_rating=0
                )
                db.add(new_item)
                db.commit()
                db.refresh(new_item)
                existing_item = new_item
                print(f"API kaynagi otomatik eklendi: {source_id} -> item_id: {new_item.item_id}")
            
            # Check existing library entry for this user/item
            existing_entry = db.query(models.UserLibrary).filter(
                models.UserLibrary.user_id == user_id,
                models.UserLibrary.item_id == existing_item.item_id
            ).first()
            
            if existing_entry:
                # Varsa, aynı library_id ile status'unu güncelle (ID değişmez!)
                if existing_entry.status == status:
                    return {
                        "success": True,
                        "message": "Bu status zaten kütüphanede var",
                        "item_id": existing_item.item_id,
                        "source_id": source_id,
                        "status": status,
                        "library_id": existing_entry.library_id
                    }
                
                # Farklı status ise, GÜNCELLE (DELETE+INSERT yerine)
                existing_entry.status = status
                db.commit()
                db.refresh(existing_entry)
                
                return {
                    "success": True,
                    "message": f"Status '{status}' olarak güncellendi (aynı ID ile)",
                    "item_id": existing_item.item_id,
                    "source_id": source_id,
                    "status": status,
                    "library_id": existing_entry.library_id
                }
            else:
                # Yeni kayıt ekle
                user_lib = models.UserLibrary(
                    user_id=user_id,
                    item_id=existing_item.item_id,
                    status=status
                )
                db.add(user_lib)
                db.commit()
                db.refresh(user_lib)
                
                return {
                    "success": True,
                    "message": f"Status '{status}' olarak eklendi (yeni ID: {user_lib.library_id})",
                    "item_id": existing_item.item_id,
                    "source_id": source_id,
                    "status": status,
                    "library_id": user_lib.library_id
                }
        
        elif action == "remove":
            # Find the item and remove from user_library
            item = db.query(models.Item).filter(
                models.Item.external_api_id == source_id
            ).first()
            
            if item:
                deleted = db.query(models.UserLibrary).filter(
                    models.UserLibrary.user_id == user_id,
                    models.UserLibrary.item_id == item.item_id,
                    models.UserLibrary.status == status
                ).delete()
                db.commit()
                
                return {
                    "success": True,
                    "message": f"API icerigi kutuphaneden kaldirildi ({deleted} kayit)",
                    "source_id": source_id,
                    "status": status,
                    "action": action,
                    "deleted_count": deleted
                }
            
            return {
                "success": True,
                "message": "Islem tamamlandi",
                "source_id": source_id,
                "status": status,
                "action": action,
                "deleted_count": 0
            }
    
    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# ============ ÖZEL LİSTELER: SİLME ============
@router.delete("/custom-lists/{list_id}")
def delete_custom_list(list_id: int, db: Session = Depends(get_db)):
    """
    Özel listeyi sil
    Silme sonrası sequence otomatik reset olur (1'den başlar)
    """
    try:
        # Listeyi bul
        custom_list = db.query(models.CustomList).filter(
            models.CustomList.list_id == list_id
        ).first()
        
        if not custom_list:
            raise HTTPException(status_code=404, detail="Liste bulunamadı")
        
        # Listeye ait tüm itemleri sil (cascade olur ama açıkça da yapalım)
        db.query(models.ListItem).filter(
            models.ListItem.list_id == list_id
        ).delete()
        
        # Listeyi sil
        db.delete(custom_list)
        db.commit()
        
        # Sequence reset et (1'den başlasın)
        # TRUNCATE kullanmıyoruz çünkü diğer listeleri silemeyiz
        # Bunun yerine, son list_id kontrol et ve sequence'i ona göre ayarla
        max_list_id = db.query(func.max(models.CustomList.list_id)).scalar()
        if max_list_id is None:
            # Hiç liste kalmadıysa 1'den başlasın (1. yeni liste ID 1 alacak)
            db.execute(text("SELECT setval('lists_list_id_seq', 1, false)"))
        else:
            # Kalan maksimum list_id'den sonra devam etsin
            db.execute(text(f"SELECT setval('lists_list_id_seq', {max_list_id}, true)"))
        
        # list_item sequence'i de reset et
        db.execute(text("SELECT setval('lists_item_list_item_id_seq', 1, false)"))
        db.commit()
        
        return {
            "success": True,
            "message": f"Liste silindi (ID: {list_id})",
            "list_id": list_id
        }
    
    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# ============ LİSTELER: İÇERİĞİ GETIR ============
@router.get("/lists/{list_id}/items")
def get_list_items(list_id: int, db: Session = Depends(get_db)):
    """
    Liste içindeki tüm itemleri getir
    list_id: İçeriğini almak istediğimiz listenin ID'si
    """
    try:
        # Liste var mı?
        custom_list = db.query(models.CustomList).filter(
            models.CustomList.list_id == list_id
        ).first()
        
        if not custom_list:
            raise HTTPException(status_code=404, detail="Liste bulunamadı")
        
        # Listedeki itemleri getir
        list_items = db.query(models.ListItem).filter(
            models.ListItem.list_id == list_id
        ).order_by(models.ListItem.position).all()
        
        # Item detaylarıyla dönüş yap
        items = []
        for list_item in list_items:
            item_data = {
                "list_item_id": list_item.list_item_id,
                "position": list_item.position,
                "source_id": list_item.source_id,
                "item_id": list_item.item_id
            }
            
            # DB itemse detaylar ekle
            if list_item.item_id:
                db_item = db.query(models.Item).filter(
                    models.Item.item_id == list_item.item_id
                ).first()
                if db_item:
                    item_data.update({
                        "title": db_item.title,
                        "item_type": db_item.item_type,
                        "year": db_item.year,
                        "poster_url": db_item.poster_url,
                        "description": db_item.description,
                        "genres": db_item.genres,
                        "external_rating": db_item.external_rating
                    })
            elif list_item.source_id:
                # API item ise source_id'den bul
                api_item = db.query(models.Item).filter(
                    models.Item.external_api_id == list_item.source_id
                ).first()
                if api_item:
                    item_data.update({
                        "title": api_item.title,
                        "item_type": api_item.item_type,
                        "year": api_item.year,
                        "poster_url": api_item.poster_url,
                        "description": api_item.description,
                        "genres": api_item.genres,
                        "external_rating": api_item.external_rating
                    })
            
            items.append(item_data)
        
        return {
            "success": True,
            "list_id": list_id,
            "list_name": custom_list.name,
            "list_description": custom_list.description,
            "is_public": custom_list.is_public,
            "created_at": custom_list.created_at.isoformat() if custom_list.created_at else None,
            "updated_at": custom_list.updated_at.isoformat() if custom_list.updated_at else None,
            "items": items,
            "item_count": len(items)
        }
    
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))