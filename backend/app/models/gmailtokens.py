from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class GmailTokens(Base):
    __tablename__ = "gmail_tokens"

    user_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("users.id"),
        primary_key=True,
    )
    access_token: Mapped[str] = mapped_column(String)
    refresh_token: Mapped[str] = mapped_column(String)

    def to_dict(self) -> dict[str, str]:
        return {
            "user_id": self.user_id,
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
        }
