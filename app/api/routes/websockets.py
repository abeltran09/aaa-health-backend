from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from helper.websocketmanager import ConnectionManager
from database import get_db
from sqlmodel import Session
from models.models import User
from typing import Annotated
from api.routes.users import get_current_user

router = APIRouter()

manager = ConnectionManager()

@router.websocket("/communicate")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_message(f"Hey there! Connection Made :) Recieved: {data}", websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.send_message("Bye!! Communication Terminated", websocket)

@router.websocket("/recive-health-batch")
async def websocket_batch_endpoint(websocket: WebSocket, db: Session = Depends(get_db)):
    await manager.connect(websocket)
    try:
        while True:
            metric_data = await websocket.receive_text()
    except WebSocketDisconnect:
         await manager.send_message("Bye!! Communication Terminated", websocket)
