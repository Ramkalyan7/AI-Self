from datetime import datetime, timezone
from typing import Literal, Optional, TYPE_CHECKING

from sqlalchemy import JSON, DateTime, ForeignKey, String
from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


if TYPE_CHECKING:
    from .user import User


CommunicationStyle = Literal["casual", "formal", "mixed"]


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class OnboardingProfile(Base):
    __tablename__ = "onboarding_profiles"

    user_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("users.id"),
        primary_key=True,
    )
    display_name: Mapped[str] = mapped_column(String)
    occupation: Mapped[str] = mapped_column(String)
    personality_description: Mapped[str] = mapped_column(String)
    communication_style: Mapped[str] = mapped_column(String, default="mixed")
    top_values: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=True)
    dislikes: Mapped[str] = mapped_column(String)
    long_form_topics: Mapped[str] = mapped_column(String)
    current_goals: Mapped[str] = mapped_column(String)
    primary_language: Mapped[str] = mapped_column(String)
    secondary_language: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    industry: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        server_default=func.now(),
        nullable=True,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=True,
    )
    completed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )
    user: Mapped[Optional["User"]] = relationship(
        back_populates="onboarding_profile"
    )

    def to_dict(self) -> dict[str, object]:
        return {
            "user_id": self.user_id,
            "display_name": self.display_name,
            "occupation": self.occupation,
            "personality_description": self.personality_description,
            "communication_style": self.communication_style,
            "top_values": self.top_values,
            "dislikes": self.dislikes,
            "long_form_topics": self.long_form_topics,
            "current_goals": self.current_goals,
            "primary_language": self.primary_language,
            "secondary_language": self.secondary_language,
            "industry": self.industry,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "completed_at": self.completed_at,
        }
