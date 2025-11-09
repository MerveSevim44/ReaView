from fastapi import APIRouter

router = APIRouter()


@router.get("/ping")
async def ping():
	"""Simple health endpoint for the auth routes."""
	return {"service": "auth", "status": "ok"}
