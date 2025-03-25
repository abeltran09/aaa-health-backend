from datetime import datetime, timedelta
import json
import uuid
from sqlmodel import Session
from sqlalchemy.sql import text
from models.models import AggregatedHealthMetrics

async def notify_frontend_clients(user_id: uuid.UUID, aggregated_data: dict, active_connections: dict):
    message = json.dumps({
        "type": "metrics_update",
        "data": aggregated_data
    })
    
    for conn_id, conn_info in active_connections.items():
        if conn_info["user_id"] == user_id and conn_info.get("type") == "frontend":
            try:
                await conn_info["websocket"].send_text(message)
                print(f"Sent update to frontend client: {conn_id}")  # Add logging
            except Exception as e:
                print(f"Error sending to client: {e}")

def aggregate_health_metrics(db: Session, user_id: uuid.UUID):
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    one_day_ago = datetime.utcnow() - timedelta(days=1)

    print(f"Aggregating metrics for user {user_id}, from {one_day_ago}")
    
    # SQL query to get heart rate metrics including the most recent value
    sql_query = text("""
    SELECT 
        COALESCE(AVG(hm.value), 0) as avg_heart_rate,
        COALESCE(MIN(hm.value), 0) as min_heart_rate,
        COALESCE(MAX(hm.value), 0) as max_heart_rate
    FROM 
        healthmetrics hm
    JOIN metricbatch mb ON 
        mb.batch_id = hm.batch_id
    WHERE 
        mb.user_id = :user_id
        AND mb.recorded_at >= :one_day_ago
    """)
    
    result = db.execute(sql_query, {
        "user_id": user_id, 
        "one_day_ago": one_day_ago
    }).first()
    
    # SQL query to get the current/most recent heart rate
    current_hr_query = text("""
    SELECT 
        hm.value as current_heart_rate
    FROM 
        healthmetrics hm
    JOIN metricbatch mb ON 
        mb.batch_id = hm.batch_id
    WHERE 
        mb.user_id = :user_id
    ORDER BY 
        mb.recorded_at DESC
    LIMIT 1
    """)
    
    current_hr_result = db.execute(current_hr_query, {
        "user_id": user_id
    }).first()
    
    # Get the heart rate values from the query results
    avg_heart_rate = float(result.avg_heart_rate) if result and result.avg_heart_rate else 0
    min_heart_rate = float(result.min_heart_rate) if result and result.min_heart_rate else 0
    max_heart_rate = float(result.max_heart_rate) if result and result.max_heart_rate else 0
    current_heart_rate = float(current_hr_result.current_heart_rate) if current_hr_result and current_hr_result.current_heart_rate else 0
    
    # Calculate new metrics
    respiratory_rate = avg_heart_rate / 4 if avg_heart_rate > 0 else 0
    
    # For Inter-beat interval (IBI), we use the current heart rate
    # IBI is measured in milliseconds, calculated as 60,000 / heart_rate
    inter_beat_interval = 60000 / current_heart_rate if current_heart_rate > 0 else 0
    
    aggregated_results = {
        "avg_heart_rate": avg_heart_rate,
        "min_heart_rate": min_heart_rate,
        "max_heart_rate": max_heart_rate,
        "current_heart_rate": current_heart_rate,
        "respiratory_rate": respiratory_rate,
        "inter_beat_interval": inter_beat_interval
    }
    
    # Update or insert into aggregated metrics table
    existing = db.query(AggregatedHealthMetrics).filter(
        AggregatedHealthMetrics.user_id == user_id,
        AggregatedHealthMetrics.date == today
    ).first()
    
    if existing:
        for key, value in aggregated_results.items():
            setattr(existing, key, value)
        existing.last_updated = datetime.utcnow()
        db.commit()
    else:
        new_aggregate = AggregatedHealthMetrics(
            user_id=user_id,
            date=today,
            last_updated=datetime.utcnow(),
            **aggregated_results
        )
        db.add(new_aggregate)
        db.commit()

    print(f"Aggregated results: {aggregated_results}")
    return aggregated_results