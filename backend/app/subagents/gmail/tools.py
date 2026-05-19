import base64

from app.core.config import get_settings
from app.db.database import get_session
from app.models import gmailtokens
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request as GoogleRequest
from googleapiclient.discovery import build
from langchain.tools import tool
from langgraph.prebuilt import ToolRuntime


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


def get_google_credentials(user_id):
    
    session=get_session()
    token_data =session.get(gmailtokens.GmailTokens,user_id)  
    token_data_dict=token_data.to_dict()

    credentials = Credentials(
        token=token_data_dict.get("access_token"),
        refresh_token=token_data_dict.get("refresh_token"),
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




#need to figure out a way to get the user's id here.


def get_gmail_service(user_id):
    credentials=get_google_credentials(user_id)
    
    service = build(
        "gmail",
        "v1",
        credentials=credentials,
        static_discovery=False
    )
    return service


@tool
async def gmail_messages(runtime:ToolRuntime):
    """This function is used to get the list of gmails"""
    
    user_id=runtime.context.user_id
    service=get_gmail_service(user_id);

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
    print_message_bodies(service,messages)
    return {
        "messages": messages
    }
    
    
    
def extract_message_body(payload):
    """
    Extract plain text body from Gmail payload.
    """

    # Direct body
    if "parts" not in payload:
        body_data = payload.get("body", {}).get("data")
        if body_data:
            return base64.urlsafe_b64decode(body_data).decode("utf-8", errors="ignore")
        return ""

    # Multipart message
    for part in payload["parts"]:
        mime_type = part.get("mimeType")

        if mime_type == "text/plain":
            body_data = part.get("body", {}).get("data")
            if body_data:
                return base64.urlsafe_b64decode(body_data).decode(
                    "utf-8",
                    errors="ignore"
                )

    return ""


def print_message_bodies(service, messages):
    """
    Fetch and print message bodies.
    """
    for msg in messages:
        msg_id = msg["id"]

        message = service.users().messages().get(
            userId="me",
            id=msg_id,
            format="full"
        ).execute()

        payload = message["payload"]

        headers = payload.get("headers", [])

        subject = next(
            (h["value"] for h in headers if h["name"] == "Subject"),
            "(No Subject)"
        )

        sender = next(
            (h["value"] for h in headers if h["name"] == "From"),
            "(Unknown Sender)"
        )

        body = extract_message_body(payload)

        print("=" * 80)
        print(f"From: {sender}")
        print(f"Subject: {subject}")
        print("-" * 80)
        print(body[:3000])  # limit output
        print()


