from sqlalchemy import Column, Integer, String, Text, DateTime, func, ForeignKey, UniqueConstraint, Index
from .database import Base


class Item(Base):
	__tablename__ = "items"

	item_id = Column(Integer, primary_key=True, index=True)
	title = Column(String(255), nullable=False)
	item_type = Column(String(20), nullable=False)  # 'book' or 'movie'
	year = Column(Integer, nullable=True)
	description = Column(Text, nullable=True)
	poster_url = Column(Text, nullable=True)
	external_api_id = Column(String(100), nullable=True)
	genres = Column(String(500), nullable=True)  # JSON string or comma-separated
	authors = Column(String(500), nullable=True)  # For books
	page_count = Column(Integer, nullable=True)  # For books
	director = Column(String(255), nullable=True)  # For movies
	actors = Column(String(500), nullable=True)  # For movies (comma-separated)
	external_api_source = Column(String(50), nullable=True)  # 'tmdb', 'google_books', etc
	external_rating = Column(Integer, nullable=True, default=0)  # API'den gelen rating (0-10)
	created_at = Column(DateTime, server_default=func.now(), nullable=False)


class Review(Base):
    __tablename__ = "reviews"

    review_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    item_id = Column(Integer, ForeignKey("items.item_id"), nullable=True)  # DB items için
    source_id = Column(String(100), nullable=True)  # API items için (tmdb_123, google_books_456)
    review_text = Column(Text, nullable=False)
    rating = Column(Integer, nullable=True)  # 1-10 puan
    created_at = Column(DateTime, server_default=func.now(), nullable=False)


class Rating(Base):
    """Ayrı ratings tablosu - sadece puanlar için"""
    __tablename__ = "ratings"

    rating_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    item_id = Column(Integer, ForeignKey("items.item_id"), nullable=False)
    score = Column(Integer, nullable=False)  # 1-10 puan
    created_at = Column(DateTime, server_default=func.now(), nullable=False)


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(128), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Activity(Base):
    __tablename__ = "activities"

    activity_id = Column(Integer, primary_key=True, index=True)
    activity_type = Column(String(50), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    item_id = Column(Integer, ForeignKey("items.item_id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Follow(Base):
    __tablename__ = "follows"

    follower_id = Column(Integer, ForeignKey("users.user_id"), primary_key=True, nullable=False)
    followee_id = Column(Integer, ForeignKey("users.user_id"), primary_key=True, nullable=False)
    followed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class UserLibrary(Base):
    """Kullanıcının kütüphane listeleri (Okudum, Okunacak, İzledim, İzlenecek)"""
    __tablename__ = "user_library"

    library_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    item_id = Column(Integer, ForeignKey("items.item_id"), nullable=False)
    status = Column(String(50), nullable=False)  # 'read', 'toread', 'watched', 'towatch'
    added_at = Column(DateTime, server_default=func.now(), nullable=False)


class CustomList(Base):
    """Kullanıcı tarafından oluşturulan listeler"""
    __tablename__ = "lists"

    list_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    is_public = Column(Integer, default=0)  # 0=private, 1=public
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)


class ListItem(Base):
    """Listelerdeki itemler (many-to-many)"""
    __tablename__ = "lists_item"

    list_item_id = Column(Integer, primary_key=True, index=True)
    list_id = Column(Integer, ForeignKey("lists.list_id"), nullable=False)
    item_id = Column(Integer, ForeignKey("items.item_id"), nullable=True)  # DB items için
    source_id = Column(String(100), nullable=True)  # API items için (tmdb_123, google_books_456)
    position = Column(Integer, default=0)  # Sıralama için
    added_at = Column(DateTime, server_default=func.now(), nullable=False)


class APILibraryItem(Base):
    """API kaynağından gelen içeriklerin kütüphane listesi (Okudum, İzledim vb.)"""
    __tablename__ = "api_library"

    library_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    source_id = Column(String(100), nullable=False)  # 'tmdb_123', 'google_books_abc', vb.
    status = Column(String(50), nullable=False)  # 'read', 'toread', 'watched', 'towatch'
    title = Column(String(255), nullable=True)  # İçerik başlığı
    item_type = Column(String(20), nullable=True)  # 'book' or 'movie'
    added_at = Column(DateTime, server_default=func.now(), nullable=False)


class PasswordResetToken(Base):
    """Şifre sıfırlama tokenları"""
    __tablename__ = "password_reset_tokens"

    token_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    token = Column(String(255), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    used_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
