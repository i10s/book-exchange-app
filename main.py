# main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from database import init_db
from routes.auth import router as auth_router
from routes.books import router as books_router
from routes.users import router as users_router
from routes.exchanges import router as exchanges_router

def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application:
      - Initialize the database on startup
      - Enable CORS
      - Disable automatic trailing‐slash redirects
      - Register auth and resource routers
      - Provide a simple root endpoint and health check
    """
    app = FastAPI(title="Book Exchange App", version="0.1.0")

    # Disable automatic redirects for trailing slashes
    app.router.redirect_slashes = False

    # Initialize database tables at startup
    app.add_event_handler("startup", init_db)

    # Enable CORS for all origins (adjust in production)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Authentication endpoints (OAuth2 password flow)
    app.include_router(auth_router, tags=["auth"])

    # Simple root endpoint (not shown in OpenAPI schema)
    @app.get("/", include_in_schema=False)
    def root():
        """
        Welcome endpoint at /
        """
        return JSONResponse({
            "message": "📚 Welcome to the Book Exchange App! Visit /docs for API documentation."
        })

    # Health check endpoint
    @app.get("/health", tags=["health"])
    def health_check():
        """
        Simple health check at /health
        """
        return {"status": "ok"}

    # Resource routers
    app.include_router(books_router,    prefix="/books",    tags=["books"])
    app.include_router(users_router,    prefix="/users",    tags=["users"])
    app.include_router(exchanges_router, prefix="/exchanges", tags=["exchanges"])

    return app

# Instantiate the application
app = create_app()
