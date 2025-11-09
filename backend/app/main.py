from fastapi import FastAPI
from .routes import auth, items, reviews, feed, users


app = FastAPI(title="ReaView API")

# Include routers from route modules. Each route module should expose an APIRouter
# object named `router`. If a module is missing `router` this will raise an
# AttributeError; to make errors clearer we check before including.
for module, prefix, tag in (
	(auth, "/auth", "Auth"),
	(items, "/items", "Items"),
	(reviews, "/reviews", "Reviews"),
	(feed, "/feed", "Feed"),
	(users, "/users", "Users"),
):
	if hasattr(module, "router"):
		app.include_router(module.router, prefix=prefix, tags=[tag])
	else:
		# If running in development you might prefer an explicit error so you
		# know a router is missing. For now we raise a helpful error message.
		raise AttributeError(f"module {module.__name__} does not define 'router'")

