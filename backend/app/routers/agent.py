import logging
from uuid import uuid4

from app.core.config import get_settings
from app.models.messageThreads import MessageThreads
from fastapi import APIRouter, Depends, HTTPException, status
from langchain_google_genai import ChatGoogleGenerativeAI
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_session
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.llm import LlmGenerateRequest, LlmGenerateResponse
from app.agent.agent import build_system_prompt_for_user, generate_text_completion
from langgraph.checkpoint.postgres import PostgresSaver
from langchain.agents import create_agent



logger = logging.getLogger(__name__)


router = APIRouter(prefix="/agent", tags=["Agent"])



@router.get("/threads")
async def get_all_message_threads(user:User=Depends(get_current_user),session:AsyncSession=Depends(get_session)):
    try:
        result= await session.execute(select(MessageThreads).where(MessageThreads.user_id==user.id))
        message_threads=result.scalars().all()
        return message_threads    
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500,detail="Internal Server Error")
    
    
    

@router.get("/messages/{thread_id}")
async def get_all_messages(thread_id:str,user:User=Depends(get_current_user),session:AsyncSession=Depends(get_session)):
    try:
        
        settings=get_settings()
        
        result=await session.execute(select(MessageThreads).where(MessageThreads.user_id==user.id,MessageThreads.message_thread_id==thread_id ))
        
        thread=result.scalar_one_or_none()
        
        if not thread:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="You cannot access this thread")

        with PostgresSaver.from_conn_string(settings.database_url) as checkpointer:
            checkpointer.setup()
            
            model = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2)

            agent = create_agent(
                model=model,
                tools=[],
                checkpointer=checkpointer
            )

            state = agent.get_state({"configurable": {"thread_id": thread_id}})
            messages = state.values.get("messages", [])
            return messages
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500,detail="Internal Server Error")
    
    
    
    

@router.post("/new")
async def create_new_message_thread(user:User=Depends(get_current_user),session:AsyncSession = Depends(get_session)):
    try:
        thread_id=str(uuid4())
        message_thread=MessageThreads(
        message_thread_id=thread_id,
        user_id=user.id
        )
        session.add(message_thread)
        await session.commit()
        await session.refresh(message_thread)
        return message_thread.message_thread_id
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500,detail="Internal Server Error")


@router.post("/generate", response_model=LlmGenerateResponse)
async def generate_text(
    payload:LlmGenerateRequest,
    user: User = Depends(get_current_user),
    session:AsyncSession=Depends(get_session)
) -> LlmGenerateResponse:
    try:    
        
        result=await session.execute(select(MessageThreads).where(MessageThreads.user_id==user.id,MessageThreads.message_thread_id==payload.thread_id ))
        
        thread=result.scalar_one_or_none()
        
        if not thread:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="You cannot access this thread")
        
        system_instruction = await build_system_prompt_for_user(session, user.id)
        response = generate_text_completion(
            user_id=user.id,
            prompt=payload.prompt,
            system_prompt=system_instruction,
            thread_id=payload.thread_id
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
