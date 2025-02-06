from fastapi import APIRouter

from api.routes import users, anthropometric, websockets

api_router = APIRouter()
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(anthropometric.router, prefix="/anthropometric", tags=["anthropometric"])
api_router.include_router(websockets.router, prefix="/aaa-health/api/v1/ws", tags=["websockets"])