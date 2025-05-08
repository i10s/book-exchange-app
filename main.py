# book_exchange_app/main.py

from fastapi import FastAPI
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.cors import CORSMiddleware

from .database import init_db
from .routers import books, users, exchanges

def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application, including:
    - Automatic database initialization on startup
    - HTTPS redirect and CORS middleware
    - Registration of API routers
    """
    app = FastAPI(title="Book Exchange App", version="0.1.0")

    # Create database tables if they don't exist
    app.add_event_handler("startup", init_db)

    # Enforce HTTPS (in production behind a proxy this may be handled elsewhere)
    app.add_middleware(HTTPSRedirectMiddleware)

    # CORS settings (allow all for now; tighten in production)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routers
    app.include_router(books.router, prefix="/books", tags=["books"])
    app.include_router(users.router, prefix="/users", tags=["users"])
    app.include_router(exchanges.router, prefix="/exchanges", tags=["exchanges"])

    @app.get("/health", tags=["health"])
    def health_check():
        """Basic health check endpoint."""
        return {"status": "ok"}

    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "book_exchange_app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
