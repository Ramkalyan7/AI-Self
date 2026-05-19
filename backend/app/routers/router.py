from fastapi import APIRouter

from app.routers import agent, auth, health, onboarding


api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(onboarding.router)
api_router.include_router(agent.router)
