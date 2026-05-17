import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_session
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.llm import LlmGenerateRequest, LlmGenerateResponse
from app.agent.agent import build_system_prompt_for_user, generate_text_completion


logger = logging.getLogger(__name__)


router = APIRouter(prefix="/llm", tags=["llm"])


@router.post("/generate", response_model=LlmGenerateResponse)
async def generate_text(
    payload: LlmGenerateRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> LlmGenerateResponse:
    try:
        _ = user
        system_instruction = await build_system_prompt_for_user(session, user.id)
        response = generate_text_completion(
            prompt=payload.prompt,
            system_prompt=system_instruction,
        )
        return response
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Unhandled error reached llm generate route.")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to reach the language model right now.",
        ) from exc
