from app.agent.agent import AvailableConnections
from app.core.config import get_settings
from app.db.database import get_session
from app.dependencies.auth import get_current_user
from app.models.user import User
from asyncpg import connect
from composio import Composio
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, ConfigDict


#toolkit and connection or connect all are same .



router=APIRouter(prefix="connections")

settings=get_settings()

@router.get("/register")
async def register(connection_name:str,user:User=Depends[get_current_user]):
    try:
        composio = Composio()
        composio_session=composio.create(user_id=user.id)
        connection_request=composio_session.authorize(connection_name,callback_url=f"{settings.backend_url}?connection_name={connection_name}")
        redirect_url = connection_request.redirect_url
        return RedirectResponse(redirect_url);
    except Exception as e:
        print(e)
        return HTTPException(status_code=500,detail="Internal Server Error")
    


@router.get("/callback")
async def connect_callback(connection_name:str,status:str):
    try:
        return RedirectResponse(f"{settings.frontend_url}/connections?connection_name={connection_name}&status={status}")
    except Exception as e:
        print(e)
        return HTTPException(status_code=500,detail="Internal Server Error")  
    
    
    
@router.get("/available")
async def get_active_connections(user:User=Depends(get_current_user)):
    try:
        available_connection_names=[]
        for connection in AvailableConnections:
            available_connection_names.append(connection)
        
        
        composio = Composio()
        composio_session=composio.create(user_id=user.id)
        
        connections = composio_session.toolkits(toolkits=available_connection_names)
        #print(connections)
        
        return connections
                
    except Exception as e:
        print(e)
        return HTTPException(status_code=500,detail="Internal Server Error")   
    
    
    
@router.get("/tools/{connection_name}")
async def get_all_tools(connection_name:str,user:User=Depends[get_current_user]):
    composio = Composio()
    tools=composio.tools.get(user.id,toolkits=[connection_name],limit=40)
    return tools


    