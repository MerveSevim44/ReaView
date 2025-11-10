from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ItemBase(BaseModel):
	title: str
	description: Optional[str] = None


class ItemCreate(ItemBase):
	pass


class ItemOut(ItemBase):
	item_id: int

	# Pydantic v2: use `model_config` with `from_attributes=True` instead of
	# the old `Config.orm_mode`. This removes the compatibility warning.
	# If you ever need to support pydantic v1 and v2 simultaneously, consider
	# a small compatibility helper or pin to a single pydantic major version.
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

