from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from helper.websocketmanager import ConnectionManager
from helper.websocketdatahandler import * 
from database import get_db
from sqlmodel import Session
from models.models import MetricBatch, HealthMetrics
from typing import Annotated
from api.routes.users import get_current_user
import uuid
import json
from datetime import datetime, timedelta
from schemas.schemas import UserIdRequest

router = APIRouter()

manager = ConnectionManager()

BATCH_TIME_LIMIT = timedelta(seconds=5)  # Adjust based on real-world needs
BATCH_SIZE_LIMIT = 10  # Number of metrics per batch before committing

# Store active WebSocket connections
active_connections = {}

@router.post("/set-user-id/")
async def set_user_id(request: UserIdRequest):
    """
    Endpoint for frontend to set the user ID on the ESP32 device
    """
    try:
        user_id = uuid.UUID(request.user_id)
        
        # Check if ESP32 is connected
        if not manager.active_connections:
            raise HTTPException(status_code=503, detail="No ESP32 devices connected")
        
        # Send user_id to all connected ESP32 devices
        # need to send user to target a specific device !! needs work but works
        message = json.dumps({"user_id": str(user_id)})
        for connection in manager.active_connections:
            await connection.send_text(message)
            
        return {"status": "success", "message": f"User ID {user_id} sent to ESP32"}
    
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

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

    batch_metrics = []  
    last_batch_time = datetime.utcnow() 

    try:
        while True:
            message = await websocket.receive_text()
            data = json.loads(message)
            
            user_id = uuid.UUID(data["user_id"])
            metrics = data["metrics"]

            batch_metrics.extend(metrics)

            if len(batch_metrics) >= BATCH_SIZE_LIMIT or (datetime.utcnow() - last_batch_time) > BATCH_TIME_LIMIT:

                metric_batch = MetricBatch(
                    user_id=user_id,
                    recorded_at=datetime.utcnow()
                )
                db.add(metric_batch)
                db.commit()
                db.refresh(metric_batch)
                
                health_metrics = [
                    HealthMetrics(
                        batch_id=metric_batch.batch_id,
                        metric_type=metric["metric_type"],
                        value=float(metric["value"]),
                        unit=metric["unit"]
                    )
                    for metric in batch_metrics
                ]

                db.bulk_save_objects(health_metrics)
                db.commit()

                batch_metrics = []
                last_batch_time = datetime.utcnow()

                await websocket.send_text(f"Received {len(health_metrics)} metrics for user {user_id}.")

    except WebSocketDisconnect:
        # Log the disconnect but don't try to send a message
        print(f"WebSocket disconnected: Client left the connection")
    finally:
        # Always remove the connection from active connections
        manager.disconnect(websocket)

'''
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "metrics": [
    {"metric_type": "temperature", "value": 36.5, "unit": "C", "recorded_at": "2025-02-18T14:30:10"}
  ]
}
'''
