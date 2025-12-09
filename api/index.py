"""
Vercel serverless function entry point for FastAPI app
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from backend.app.routes import auth, items, reviews, feed, users, external, follows, likes
from backend.app.database import init_db
from pathlib import Path
import os

app = FastAPI(title="ReaView API")

# === CORS CONFIGURATION (MUST be FIRST - before routes) ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup (only once in serverless)
# Note: init_db with migrations might not work well in serverless
# Consider using a proper migration tool or pre-migrated database
@app.on_event("startup")
def startup_event():
    # For serverless, you may want to skip migrations
    # and ensure your database is already migrated
    try:
        init_db()
        print("[OK] Application started")
    except Exception as e:
        print(f"[WARNING] Could not run migrations in serverless: {e}")

# Mount avatars directory as static files
avatars_dir = Path(__file__).parent.parent / "backend" / "avatars"
if avatars_dir.exists():
    app.mount("/avatars", StaticFiles(directory=str(avatars_dir)), name="avatars")

# Include routers from route modules
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
        raise AttributeError(f"module {module.__name__} does not define 'router'")

# Health check endpoint
@app.get("/")
@app.get("/health")
def health_check():
    return {"status": "[OK] ReaView API is running on Vercel"}

# Export the app for Vercel
handler = app
