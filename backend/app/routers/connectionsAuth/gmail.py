import logging
from app.core.config import  get_settings
from app.db.database import get_session
from app.models.gmailtokens import GmailTokens
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, Request,status
from authlib.integrations.starlette_client import OAuth
from fastapi.responses import  RedirectResponse
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
    try:
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
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Error while logging in")
    
    
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
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="error while authenticating users gmail account")

