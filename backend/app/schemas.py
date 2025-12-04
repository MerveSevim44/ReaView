from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ItemBase(BaseModel):
	title: str
	description: Optional[str] = None


class ItemCreate(ItemBase):
	item_type: str = 'book'
	year: Optional[int] = None
	poster_url: Optional[str] = None
	external_api_id: Optional[str] = None
	genres: Optional[str] = None
	authors: Optional[str] = None
	page_count: Optional[int] = None
	director: Optional[str] = None
	actors: Optional[str] = None
	external_api_source: Optional[str] = None
	external_rating: Optional[int] = None  # API'den gelen rating (0-10)


class ItemOut(ItemBase):
	item_id: int
	item_type: Optional[str] = None
	year: Optional[int] = None
	poster_url: Optional[str] = None
	external_api_id: Optional[str] = None
	genres: Optional[str] = None
	authors: Optional[str] = None
	page_count: Optional[int] = None
	director: Optional[str] = None
	actors: Optional[str] = None
	external_api_source: Optional[str] = None
	created_at: Optional[datetime] = None
	external_rating: Optional[int] = 0  # API'den gelen rating (0-10)
	user_rating: Optional[float] = 0  # Kullanıcı reviews'lerinden ortalama
	combined_rating: Optional[float] = 0  # Hibrid rating (average)
	review_count: Optional[int] = None  # Number of reviews
	popularity: Optional[int] = None  # Based on review count

	model_config = {"from_attributes": True}

class ReviewCreate(BaseModel):
    user_id: int
    item_id: Optional[int] = None
    review_text: str
    rating: Optional[int] = None  # 1-10


class ReviewOut(BaseModel):
	review_id: int
	user_id: int
	item_id: Optional[int] = None
	review_text: str
	rating: Optional[int] = None
	created_at: Optional[datetime] = None
	username: Optional[str] = None
	avatar_url: Optional[str] = None

	model_config = {"from_attributes": True}


class ReviewUpdate(BaseModel):
	review_text: Optional[str] = None
	rating: Optional[int] = None


class RatingOut(BaseModel):
	"""Ratings tablosundan çekilen puanlar"""
	rating_id: int
	user_id: int
	item_id: int
	score: int  # 1-10 puan
	created_at: Optional[datetime] = None
	username: Optional[str] = None
	avatar_url: Optional[str] = None

	model_config = {"from_attributes": True}


class UserOut(BaseModel):
	user_id: int
	username: str
	email: str
	bio: Optional[str] = None
	avatar_url: Optional[str] = None
	created_at: Optional[datetime] = None

	model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
	bio: Optional[str] = None
	avatar_url: Optional[str] = None


class UserRegister(BaseModel):
	username: str
	email: str
	password: str


class UserLogin(BaseModel):
	email: str
	password: str


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
	user_id: Optional[int] = None
	item_id: Optional[int] = None

	model_config = {"from_attributes": True}


class FollowCreate(BaseModel):
	follower_id: int
	followee_id: int


class FollowOut(BaseModel):
	follower_id: int
	followee_id: int
	followed_at: Optional[datetime] = None

	model_config = {"from_attributes": True}


class UserWithFollowInfo(UserOut):
	"""User ile follow bilgisi"""
	is_following: Optional[bool] = False
	followers_count: Optional[int] = 0
	following_count: Optional[int] = 0

	model_config = {"from_attributes": True}


# ============== PASSWORD RESET SCHEMAS ==============

class ForgotPasswordRequest(BaseModel):
	"""Şifre sıfırlama isteği"""
	email: str


class ResetPasswordRequest(BaseModel):
	"""Şifre sıfırlama"""
	email: str
	token: str
	new_password: str
