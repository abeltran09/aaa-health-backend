from fastapi import APIRouter

from api.routes import users, anthropometric

api_router = APIRouter()
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(anthropometric.router, prefix="/anthropometric", tags=["anthropometric"])