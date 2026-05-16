from app.routers.connectionsAuth import gmail
from fastapi import APIRouter

from app.routers import auth, health, llm, onboarding


api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(onboarding.router)
api_router.include_router(llm.router)
api_router.include_router(gmail.router)
