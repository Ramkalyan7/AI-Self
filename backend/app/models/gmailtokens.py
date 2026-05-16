from sqlmodel import Field, SQLModel

class GmailTokens(SQLModel, table=True):
    model_config = {"extra": "ignore"}

    __tablename__ = "gmail_tokens"

    user_id: str = Field(primary_key=True, foreign_key="users.id")
    access_token:str
    refresh_token:str
