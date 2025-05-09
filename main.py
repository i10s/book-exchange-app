# main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from starlette.staticfiles import StaticFiles

from database import init_db
from routes.auth import router as auth_router
from routes.books import router as books_router
from routes.users import router as users_router
from routes.exchanges import router as exchanges_router

def create_app() -> FastAPI:
    app = FastAPI(title="Book Exchange App", version="0.1.0")
    app.router.redirect_slashes = False

    # 1️⃣ Initialize database on startup
    app.add_event_handler("startup", init_db)

    # 2️⃣ CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 3️⃣ API routers
    app.include_router(auth_router,     prefix="/auth",     tags=["auth"])
    app.include_router(books_router,    prefix="/books",    tags=["books"])
    app.include_router(users_router,    prefix="/users",    tags=["users"])
    app.include_router(exchanges_router,prefix="/exchanges", tags=["exchanges"])

    # 4️⃣ Health check BEFORE static mount
    @app.get("/health", tags=["health"])
    def health_check():
        """
        Simple health check endpoint.
        """
        return {"status": "ok"}

    # 5️⃣ Serve SPA & assets (catch-all)
    app.mount(
        "/",
        StaticFiles(directory="client", html=True),
        name="static",
    )

    return app

# Instantiate the application
app = create_app()
