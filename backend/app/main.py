from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import auth, items, reviews, feed, users, external, follows


app = FastAPI(title="ReaView API")

# Enable CORS so frontend can call backend from browser
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev; in production use specific origins like ["https://yourdomain.com"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
):
	if hasattr(module, "router"):
		app.include_router(module.router, prefix=prefix, tags=[tag])
	else:
		# If running in development you might prefer an explicit error so you
		# know a router is missing. For now we raise a helpful error message.
		raise AttributeError(f"module {module.__name__} does not define 'router'")
