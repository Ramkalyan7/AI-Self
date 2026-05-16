from app.core.config import get_settings
from app.db.database import get_session
from app.models import gmailtokens
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request as GoogleRequest
from googleapiclient.discovery import build


settings=get_settings()

SCOPES = [
    "openid",
    "email",
    "profile",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.compose",
     "https://www.googleapis.com/auth/gmail.modify",
      "https://www.googleapis.com/auth/gmail.send",
]


def get_google_credentials(token_data):

    credentials = Credentials(
        token=token_data.get("access_token"),
        refresh_token=token_data.get("refresh_token"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=settings.google_oauth_client_id,
        client_secret=settings.google_oauth_client_secret,
        scopes=SCOPES
    )

    # auto refresh expired token
    if credentials.expired and credentials.refresh_token:

        credentials.refresh(
            GoogleRequest()
        )

    return credentials




async def gmail_messages(user_id:str):
    session=get_session()
    token_data =session.get(gmailtokens.GmailTokens,user_id)  
    token_data_dict=token_data.model_dump()
    credentials = get_google_credentials(
        token_data_dict
    )
    service = build(
        "gmail",
        "v1",
        credentials=credentials
    )

    results = (
        service.users()
        .messages()
        .list(
            userId="me",
            maxResults=10
        )
        .execute()
    )

    messages = results.get("messages", [])

    return {
        "messages": messages
    }

