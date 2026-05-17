import logging

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.security import decode_access_token
from app.db.database import AsyncSessionLocal
from app.repositories.user import get_user_by_id


logger = logging.getLogger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)
        self.public_paths = {
            "/",
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/auth/login",
            "/auth/signup",
            "/auth/gmail/login",
            "/auth/gmail/callback"
        }

    async def dispatch(self, request: Request, call_next):
        request.state.user = None
        if request.url.path in self.public_paths:
            return await call_next(request)

        authorization = request.headers.get("Authorization")
        if not authorization:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Authentication is required."},
            )

        scheme, _, token = authorization.partition(" ")
        if scheme.lower() != "bearer" or not token:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Authentication is required."},
            )

        payload = decode_access_token(token)
        if payload is None:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Authentication is required."},
            )

        subject = payload.get("sub")
        if subject is None:
            logger.warning("JWT token subject is missing or invalid.")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Authentication is required."},
            )

        try:
            async with AsyncSessionLocal() as session:
                user = await get_user_by_id(session, str(subject))
            if user is None:
                logger.warning("JWT token references a missing user.")
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "Authentication is required."},
                )

            request.state.user = user
            return await call_next(request)
        except Exception:
            logger.exception("Failed to authenticate request.")
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={"detail": "Unable to process the request right now."},
            )
