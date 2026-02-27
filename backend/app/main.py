from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .routes import auth, items, reviews, feed, users, external, follows, likes
from sqlalchemy import text
from .database import SessionLocal, engine, init_db
from pathlib import Path


app = FastAPI(title="ReaView API")

# === CORS CONFIGURATION (MUST be FIRST - before routes) ===
# Use built-in CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # allow everything
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
def startup_event():
	init_db()
	print("[OK] Application started")

# Mount avatars directory as static files
avatars_dir = Path(__file__).parent.parent / "avatars"
if avatars_dir.exists():
    app.mount("/avatars", StaticFiles(directory=str(avatars_dir)), name="avatars")

# Include routers from route modules. Each route module should expose an APIRouter
# object named `router`. If a module is missing `router` this will raise an
# AttributeError; to make errors clearer we check before including.
for module, prefix, tag in (
	(auth, "/auth", "Auth"),
	(items, "/items", "Items"),
	(reviews, "/reviews", "Reviews"),
	(feed, "/feed", "Feed"),
	(users, "/users", "Users"),
	(external, "/external", "External API"),
	(follows, "/users", "Follow System"),
	(likes, "/likes", "Likes"),
):
	if hasattr(module, "router"):
		app.include_router(module.router, prefix=prefix, tags=[tag])
	else:
		# If running in development you might prefer an explicit error so you
		# know a router is missing. For now we raise a helpful error message.
		raise AttributeError(f"module {module.__name__} does not define 'router'")


# Migration endpoint - çalıştırmak için: POST /migrate
@app.post("/migrate")
def run_migrations():
	"""
	Run all migration files in sequential order.
	Only for development - do not use in production.
	"""
	migrations_dir = Path(__file__).parent.parent / "migrations"
	migration_files = sorted(migrations_dir.glob("*.sql"))
	
	if not migration_files:
		return {"message": "No migration files found", "count": 0}
	
	db = SessionLocal()
	results = []
	
	try:
		for migration_file in migration_files:
			try:
				with open(migration_file, "r") as f:
					sql_content = f.read()
				
				# Execute SQL
				db.execute(text(sql_content))
				db.commit()
				results.append({
					"file": migration_file.name,
					"status": "[OK] Success"
				})
			except Exception as e:
				results.append({
					"file": migration_file.name,
					"status": f"[WARNING] {str(e)}"
				})
				db.rollback()
		
		return {
			"message": "Migration process completed",
			"total": len(migration_files),
			"results": results
		}
	finally:
		db.close()


# Health check endpoint
@app.get("/health")
def health_check():
	return {"status": "[OK] ReaView API is running"}

