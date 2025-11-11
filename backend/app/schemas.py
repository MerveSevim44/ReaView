from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ItemBase(BaseModel):
	title: str
	description: Optional[str] = None


class ItemCreate(ItemBase):
	item_type: str = 'book'  # 'movie' or 'book'
	year: Optional[int] = None
	poster_url: Optional[str] = None
	genres: Optional[str] = None
	authors: Optional[str] = None  # For books
	page_count: Optional[int] = None  # For books
	director: Optional[str] = None  # For movies
	actors: Optional[str] = None  # For movies
	external_api_source: Optional[str] = None


class ItemOut(ItemBase):
	item_id: int
	item_type: str
	year: Optional[int] = None
	poster_url: Optional[str] = None
	genres: Optional[str] = None
	authors: Optional[str] = None
	page_count: Optional[int] = None
	director: Optional[str] = None
	actors: Optional[str] = None
	created_at: Optional[datetime] = None
	updated_at: Optional[datetime] = None
	external_api_source: Optional[str] = None

	model_config = {"from_attributes": True}

class ReviewCreate(BaseModel):
    user_id: int
    item_id: int
    review_text: str


class ReviewOut(BaseModel):
	review_id: int
	user_id: int
	item_id: int
	review_text: str
	# Use a datetime type so Pydantic accepts SQLAlchemy datetime objects
	created_at: Optional[datetime] = None

	model_config = {"from_attributes": True}


class UserOut(BaseModel):
	user_id: int
	username: str
	email: str
	created_at: Optional[datetime] = None

	model_config = {"from_attributes": True}


class ActivityOut(BaseModel):
	activity_id: int
	activity_type: str
	user_id: int
	item_id: Optional[int] = None
	created_at: Optional[datetime] = None

	model_config = {"from_attributes": True}


class ActivityWithDetailsOut(BaseModel):
	"""Activity with joined user and item details (denormalized for convenience)"""
	activity_id: int
	activity_type: str
	created_at: Optional[datetime] = None
	username: Optional[str] = None
	title: Optional[str] = None
	item_type: Optional[str] = None

	model_config = {"from_attributes": True}

