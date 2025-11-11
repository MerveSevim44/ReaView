from fastapi import APIRouter

router = APIRouter()


@router.get("/ping")
async def ping():
	"""Simple health endpoint for the auth routes."""
	return {"service": "auth", "status": "ok"}

# bu kısımda getCurrentUser fonksiyonu eklenebilir 
# const currentUserId = 1;
#yerine gerçek bir giriş mekanizması geldiğinde (örneğin auth.js içind
												#bundan dolayı