from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_session
from app.schemas.health import HealthResponse


router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse, summary="Health check")
async def health_check(session: AsyncSession = Depends(get_session)) -> HealthResponse:
    await session.execute(text("select 1"))
    return HealthResponse(status="ok", database="connected")
    
