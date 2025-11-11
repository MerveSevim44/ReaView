from sqlalchemy import Column, Integer, String, Text, DateTime, func, ForeignKey, UniqueConstraint, Index
from .database import Base


class Item(Base):
	__tablename__ = "items"

	item_id = Column(Integer, primary_key=True, index=True)
	title = Column(String(256), nullable=False, index=True)
	description = Column(Text, nullable=True)
	
	# External API Integration Fields
	item_type = Column(String(10), nullable=False, default='book')  # 'movie' or 'book'
	year = Column(Integer, nullable=True)
	poster_url = Column(String(512), nullable=True)
	genres = Column(Text, nullable=True)  # Comma-separated genres
	
	# Book-specific fields
	authors = Column(Text, nullable=True)  # Comma-separated author names
	page_count = Column(Integer, nullable=True)
	
	# Movie-specific fields
	director = Column(String(256), nullable=True)
	actors = Column(Text, nullable=True)  # Comma-separated actor names
	
	# Metadata
	created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
	updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
	external_api_source = Column(String(50), nullable=True)  # 'tmdb', 'google_books', 'openlibrary'
	
	# Unique constraint to prevent duplicate imports
	__table_args__ = (
		UniqueConstraint('title', 'item_type', name='uix_item_title_type'),
		Index('idx_title_type', 'title', 'item_type'),
		Index('idx_item_type', 'item_type'),
		Index('idx_year', 'year'),
	)


class Review(Base):
    __tablename__ = "reviews"

    review_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    item_id = Column(Integer, ForeignKey("items.item_id"), nullable=False)
    review_text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(128), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
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
