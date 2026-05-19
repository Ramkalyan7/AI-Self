from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.onboarding import OnboardingProfile
from app.repositories.onboarding import (
    get_onboarding_profile_by_user_id,
    upsert_onboarding_profile,
)
from app.schemas.onboarding import (
    OnboardingProfileResponse,
    OnboardingProfileUpsertRequest,
    OnboardingStatusResponse,
)


def _to_response(profile: OnboardingProfile) -> OnboardingProfileResponse:
    return OnboardingProfileResponse(
        **profile.to_dict()
    )





async def get_onboarding_status(
    session: AsyncSession,
    user_id: str,
) -> OnboardingStatusResponse:
    profile = await get_onboarding_profile_by_user_id(session, user_id)
    if profile is None:
        return OnboardingStatusResponse(completed=False, profile=None)
    return OnboardingStatusResponse(completed=True, profile=_to_response(profile))


async def save_onboarding_profile(
    *,
    session: AsyncSession,
    user_id: str,
    payload: OnboardingProfileUpsertRequest,
) -> OnboardingProfileResponse:
    try:
        profile = await upsert_onboarding_profile(
            session=session,
            user_id=user_id,
            profile=payload.model_dump(),
        )
        return _to_response(profile)
    except Exception as exc:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to save onboarding right now.",
        ) from exc
