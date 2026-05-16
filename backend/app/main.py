from fastapi import FastAPI
import uvicorn

from app.core.config import get_settings
from app.middleware.auth import AuthMiddleware
from app.routers.router import api_router
from starlette.middleware.sessions import SessionMiddleware


settings = get_settings()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )
    
    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.jwt_secret_key,
    )
     
    app.add_middleware(AuthMiddleware)

    app.include_router(api_router)
    return app


app = create_app()


def run() -> None:
    uvicorn.run(
        "app.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.is_development,
    )
