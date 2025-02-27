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

router = APIRouter()

manager = ConnectionManager()

BATCH_TIME_LIMIT = timedelta(seconds=5)  # Adjust based on real-world needs
BATCH_SIZE_LIMIT = 10  # Number of metrics per batch before committing

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
         await manager.send_message("Bye!! Communication Terminated", websocket)
