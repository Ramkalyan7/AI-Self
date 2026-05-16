import logging
from app.core.config import  get_settings
from app.db.database import get_session
from app.dependencies.auth import get_current_user
from app.models.gmailtokens import GmailTokens
from app.models.user import User
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, Request
from authlib.integrations.starlette_client import OAuth
from fastapi.responses import JSONResponse, RedirectResponse
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request as GoogleRequest
from sqlalchemy.ext.asyncio import AsyncSession





logger=logging.getLogger(__name__)

load_dotenv()

router = APIRouter(prefix="/auth/gmail", tags=["Gmail OAuth"])

oauth = OAuth()

SCOPES = [
    "openid",
    "email",
    "profile",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.compose",
     "https://www.googleapis.com/auth/gmail.modify",
      "https://www.googleapis.com/auth/gmail.send",
]

settings = get_settings()

oauth.register(
    name="google",
    client_id=settings.google_oauth_client_id,
    client_secret=settings.google_oauth_client_secret,
    server_metadata_url=(
        "https://accounts.google.com/"
        ".well-known/openid-configuration"
    ),
    client_kwargs={
        "scope": " ".join(SCOPES)
    }
)

#need to activate authmiddleware here
#need to send actual user id here


@router.get("/login")
async def google_login(request: Request):

    redirect_uri = request.url_for(
        "google_callback"
    )
    
    request.session["app_user_id"] = 0

    return await oauth.google.authorize_redirect(
        request,
        redirect_uri,
        access_type="offline",
        prompt="consent",
    )
    
    
@router.get("/callback")
async def google_callback(request: Request,session: AsyncSession = Depends(get_session)):
    try:
        token = await oauth.google.authorize_access_token(
            request
        )

        user_id=request.session.get("app_user_id")
        access_token=token.get("access_token")
        refresh_token=token.get("refresh_token")
    
        #2) store the tokens corresponding to the user id
        gmailTokens = GmailTokens(
            user_id=user_id,
            access_token=access_token,
            refresh_token=refresh_token
        )
        session.add(gmailTokens)
        await session.commit()
        await session.refresh(gmailTokens)
        return RedirectResponse(
            url=f"{settings.frontend_url}"
        )
    except Exception as e:
        logger.error(e)
        return JSONResponse({"error":"some error occurred"})



# # ---------------------------------------------------
# # Build Google Credentials
# # ---------------------------------------------------

# def get_google_credentials(token_data):

#     credentials = Credentials(
#         token=token_data["access_token"],
#         refresh_token=token_data.get("refresh_token"),
#         token_uri="https://oauth2.googleapis.com/token",
#         client_id=GOOGLE_CLIENT_ID,
#         client_secret=GOOGLE_CLIENT_SECRET,
#         scopes=SCOPES
#     )

#     # auto refresh expired token
#     if credentials.expired and credentials.refresh_token:

#         credentials.refresh(
#             GoogleRequest()
#         )

#     return credentials


# # ---------------------------------------------------
# # Gmail Messages
# # ---------------------------------------------------

# @app.get("/gmail/messages")
# async def gmail_messages(request: Request):

#     token_data = request.session.get("token")

#     if not token_data:
#         return JSONResponse(
#             status_code=401,
#             content={
#                 "message": "Not authenticated"
#             }
#         )

#     credentials = get_google_credentials(
#         token_data
#     )

#     service = build(
#         "gmail",
#         "v1",
#         credentials=credentials
#     )

#     results = (
#         service.users()
#         .messages()
#         .list(
#             userId="me",
#             maxResults=10
#         )
#         .execute()
#     )

#     messages = results.get("messages", [])

#     return {
#         "messages": messages
#     }


# # ---------------------------------------------------
# # Single Email Details
# # ---------------------------------------------------

# @app.get("/gmail/message/{message_id}")
# async def gmail_message(
#     message_id: str,
#     request: Request
# ):

#     token_data = request.session.get("token")

#     if not token_data:
#         return JSONResponse(
#             status_code=401,
#             content={
#                 "message": "Not authenticated"
#             }
#         )

#     credentials = get_google_credentials(
#         token_data
#     )

#     service = build(
#         "gmail",
#         "v1",
#         credentials=credentials
#     )

#     message = (
#         service.users()
#         .messages()
#         .get(
#             userId="me",
#             id=message_id
#         )
#         .execute()
#     )

#     return message


