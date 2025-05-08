# main.py

from fastapi import FastAPI
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.cors import CORSMiddleware

from database import init_db
from routes.books import router as books_router
from routes.users import router as users_router
from routes.exchanges import router as exchanges_router

def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application:
    - Initialize the database on startup
    - Enforce HTTPS redirect
    - Enable CORS
    - Register API routers
    """
    app = FastAPI(title="Book Exchange App", version="0.1.0")

    # Auto-create database tables at startup
    app.add_event_handler("startup", init_db)

    # Redirect HTTP to HTTPS (if exposed)
    # app.add_middleware(HTTPSRedirectMiddleware)

    # Allow all CORS origins for now
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routers
    app.include_router(books_router,    prefix="/books",    tags=["books"])
    app.include_router(users_router,    prefix="/users",    tags=["users"])
    app.include_router(exchanges_router, prefix="/exchanges", tags=["exchanges"])

    @app.get("/health", tags=["health"])
    def health_check():
        """Simple health check endpoint."""
        return {"status": "ok"}

    return app

app = create_app()
