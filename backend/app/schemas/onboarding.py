from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator

from app.models.onboarding import CommunicationStyle


ShortText = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=255),
]
LongText = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=2000),
]


class OnboardingProfileUpsertRequest(BaseModel):
    display_name: ShortText = Field(max_length=255)
    occupation: ShortText = Field(max_length=255)
    personality_description: LongText = Field(max_length=2000)
    communication_style: CommunicationStyle
    top_values: list[ShortText] = Field(min_length=3, max_length=3)
    dislikes: LongText = Field(max_length=2000)
    long_form_topics: LongText = Field(max_length=2000)
    current_goals: LongText = Field(max_length=2000)
    primary_language: ShortText = Field(max_length=255)
    secondary_language: ShortText | None = None
    industry: ShortText = Field(max_length=255)

    @field_validator("top_values")
    @classmethod
    def validate_top_values(cls, values: list[str]) -> list[str]:
        normalized_values = [value.strip() for value in values]
        if len(set(value.lower() for value in normalized_values)) != len(
            normalized_values
        ):
            raise ValueError("Top values must be unique.")
        return normalized_values


class OnboardingProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: str
    display_name: str
    occupation: str
    personality_description: str
    communication_style: CommunicationStyle
    top_values: list[str]
    dislikes: str
    long_form_topics: str
    current_goals: str
    primary_language: str
    secondary_language: str | None
    industry: str
    completed_at: datetime
    created_at: datetime
    updated_at: datetime


class OnboardingStatusResponse(BaseModel):
    completed: bool
    profile: OnboardingProfileResponse | None
