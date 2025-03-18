from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from helper.websocketmanager import ConnectionManager
from helper.websocketdatahandler import aggregate_health_metrics, notify_frontend_clients
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

BATCH_TIME_LIMIT = timedelta(seconds=5)
BATCH_SIZE_LIMIT = 10  

# Store active WebSocket connections
active_connections = {}

@router.post("/set-user-id/")
async def set_user_id(request: UserIdRequest):
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

@router.post("/disconnect-device/")
async def disconnect_device(request: UserIdRequest):
    try:
        user_id = uuid.UUID(request.user_id)
        
        # Check if ESP32 is connected
        if not manager.active_connections:
            raise HTTPException(status_code=503, detail="No ESP32 devices connected")
        
        # Send disconnect command to all connected ESP32 devices
        message = json.dumps({"command": "disconnect", "user_id": str(user_id)})
        for connection in manager.active_connections:
            await connection.send_text(message)
            
        return {"status": "success", "message": f"Disconnect command sent for User ID {user_id}"}
    
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.websocket("/recive-health-batch")
async def websocket_batch_endpoint(websocket: WebSocket, db: Session = Depends(get_db)):
    await manager.connect(websocket)

    connection_id = id(websocket)
    user_connection = None

    batch_metrics = []  
    last_batch_time = datetime.utcnow() 

    try:
        while True:
            message = await websocket.receive_text()
            data = json.loads(message)
            
            user_id = uuid.UUID(data["user_id"])
            metrics = data["metrics"]

            # Store user connection for frontend notifications
            if not user_connection:
                user_connection = user_id
                active_connections[connection_id] = {"websocket": websocket, "user_id": user_id}

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

                aggregated_data = aggregate_health_metrics(db, user_id)

                await notify_frontend_clients(user_id, aggregated_data, active_connections)

                batch_metrics = []
                last_batch_time = datetime.utcnow()

                await websocket.send_text(f"Received {len(health_metrics)} metrics for user {user_id}.")

    except WebSocketDisconnect:
        # Log the disconnect but don't try to send a message
        print(f"WebSocket disconnected: Client left the connection")
    finally:
        # Always remove the connection from active connections
        if connection_id in active_connections:
            del active_connections[connection_id]
        manager.disconnect(websocket)


@router.websocket("/frontend-updates")
async def frontend_websocket_endpoint(
    websocket: WebSocket, 
    db: Session = Depends(get_db)
    ):
    await manager.connect(websocket)
    query_params = websocket.query_params
    user_id = query_params.get("user_id")

    if not user_id:
        print("WebSocket connection closed: user_id is missing")  # Log missing user_id
        await websocket.close()
        return
    
    try:
        user_uuid = uuid.UUID(user_id)
        connection_id = id(websocket)
        active_connections[connection_id] = {"websocket": websocket, "user_id": user_uuid, "type": "frontend"}
        
        # Send initial data
        initial_data = aggregate_health_metrics(db, user_uuid)
        await websocket.send_text(json.dumps({
            "type": "metrics_update",
            "data": initial_data
        }))
        
        # Keep connection alive
        while True:
            # Wait for any message (including ping/pong)
            await websocket.receive_text()
            
    except WebSocketDisconnect:
        print(f"Frontend WebSocket disconnected: {connection_id}")
    except ValueError:
        print(f"Invalid user_id in WebSocket connection")
    finally:
        if connection_id in active_connections:
            del active_connections[connection_id]
        manager.disconnect(websocket)

'''
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "metrics": [
    {"metric_type": "temperature", "value": 36.5, "unit": "C", "recorded_at": "2025-02-18T14:30:10"}
  ]
}
'''