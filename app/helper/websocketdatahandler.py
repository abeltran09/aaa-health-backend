from datetime import datetime, timedelta
import json
import uuid
from sqlmodel import Session
from sqlalchemy.sql import text
from models.models import AggregatedHealthMetrics
import numpy as np

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

# New function to notify clients specifically about daily data
async def notify_daily_metrics(user_id: uuid.UUID, daily_data: dict, active_connections: dict):
    message = json.dumps({
        "type": "daily_metrics_update",
        "data": daily_data
    })
    
    for conn_id, conn_info in active_connections.items():
        if conn_info["user_id"] == user_id and conn_info.get("type") == "daily_frontend":
            try:
                await conn_info["websocket"].send_text(message)
                print(f"Sent daily update to frontend client: {conn_id}")
            except Exception as e:
                print(f"Error sending daily data to client: {e}")

def aggregate_health_metrics(db: Session, user_id: uuid.UUID):
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    one_day_ago = datetime.utcnow() - timedelta(days=1)
    seven_days_ago = today - timedelta(days=7)

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
        AND hm.metric_type = 'heart rate'
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
        AND hm.metric_type = 'heart rate'
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

     # Add a new query to get consecutive heart rate measurements for HRV calculation
    hrv_query = text("""
    SELECT 
        hm.value as heart_rate,
        mb.recorded_at
    FROM 
        healthmetrics hm
    JOIN metricbatch mb ON 
        mb.batch_id = hm.batch_id
    WHERE 
        mb.user_id = :user_id
        AND hm.metric_type = 'heart rate'
        AND mb.recorded_at >= :one_day_ago
    ORDER BY 
        mb.recorded_at ASC
    """)
    
    hrv_results = db.execute(hrv_query, {
        "user_id": user_id,
        "one_day_ago": one_day_ago
    }).fetchall()
    
    # Calculate HRV (using SDNN method - standard deviation of NN intervals)
    ibi_values = []
    for row in hrv_results:
        # Convert heart rate to IBI in milliseconds
        if row.heart_rate > 0:
            ibi = 60000 / row.heart_rate
            ibi_values.append(ibi)
    
    # Calculate heart rate variability (standard deviation of IBI values)
    heart_rate_variability = 0
    if len(ibi_values) > 1:
        heart_rate_variability = float(np.std(ibi_values))
    
    # Calculate average HRV (could be a rolling average or daily average)
    # Get previous HRV values from the last 7 days
    avg_hrv_query = text("""
    SELECT 
        AVG(heart_rate_variability) as avg_heart_rate_variability
    FROM 
        aggregatedhealthmetrics
    WHERE 
        user_id = :user_id
        AND date >= :seven_days_ago
        AND date < :today
    """)
    
    avg_hrv_result = db.execute(avg_hrv_query, {
        "user_id": user_id,
        "seven_days_ago": seven_days_ago,
        "today": today
    }).first()
    
    # Get the average HRV from the query result
    avg_heart_rate_variability = float(avg_hrv_result.avg_heart_rate_variability) if avg_hrv_result and avg_hrv_result.avg_heart_rate_variability else 0
    
    # Combine all metrics in the aggregated results
    aggregated_results = {
        "avg_heart_rate": avg_heart_rate,
        "min_heart_rate": min_heart_rate,
        "max_heart_rate": max_heart_rate,
        "current_heart_rate": current_heart_rate,
        "respiratory_rate": respiratory_rate,
        "inter_beat_interval": inter_beat_interval,
        "heart_rate_variability": heart_rate_variability,
        "avg_heart_rate_variability": avg_heart_rate_variability
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

# New function to aggregate hourly metrics for the current day
def aggregate_daily_hourly_metrics(db: Session, user_id: uuid.UUID):
    """Aggregate health metrics by hour for the current day"""
    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)
    
    # SQL query to get hourly heart rate data
    hourly_heart_rate_query = text("""
    SELECT 
        EXTRACT(HOUR FROM mb.recorded_at) as hour,
        COALESCE(AVG(hm.value), 0) as avg_heart_rate
    FROM 
        healthmetrics hm
    JOIN metricbatch mb ON 
        mb.batch_id = hm.batch_id
    WHERE 
        mb.user_id = :user_id
        AND mb.recorded_at >= :today
        AND mb.recorded_at < :tomorrow
        AND hm.metric_type = 'heart_rate'
    GROUP BY 
        EXTRACT(HOUR FROM mb.recorded_at)
    ORDER BY 
        hour
    """)
    
    heart_rate_results = db.execute(hourly_heart_rate_query, {
        "user_id": user_id,
        "today": today,
        "tomorrow": tomorrow
    }).fetchall()
    
    # SQL query to get hourly HRV data
    hourly_hrv_query = text("""
    SELECT  
        EXTRACT(HOUR FROM mb.recorded_at) as hour,
        COALESCE(AVG(hm.value), 0) as avg_ibi
    FROM 
        healthmetrics hm
    JOIN metricbatch mb ON 
        mb.batch_id = hm.batch_id
    WHERE 
        mb.user_id = :user_id
        AND mb.recorded_at >= :today
        AND mb.recorded_at < :tomorrow
        AND hm.metric_type = 'inter_beat_interval'  -- use the IBI metric type
    GROUP BY 
        EXTRACT(HOUR FROM mb.recorded_at)
    ORDER BY 
        hour
    """)
    
    hrv_results = db.execute(hourly_hrv_query, {
        "user_id": user_id,
        "today": today,
        "tomorrow": tomorrow
    }).fetchall()
    
    # Get the latest heart rate and HRV
    latest_metrics_query = text("""
    SELECT 
        hm.metric_type,
        hm.value,
        mb.recorded_at
    FROM 
        healthmetrics hm
    JOIN metricbatch mb ON 
        mb.batch_id = hm.batch_id
    WHERE 
        mb.user_id = :user_id
        AND (hm.metric_type = 'heart_rate' OR hm.metric_type = 'hrv')
    ORDER BY 
        mb.recorded_at DESC
    LIMIT 2
    """)
    
    latest_results = db.execute(latest_metrics_query, {
        "user_id": user_id
    }).fetchall()
    
    # Process the hourly data
    hours = []
    heart_rates = []
    hrvs = []
    
    # Initialize with zeros for each hour
    current_hour = datetime.now().hour
    for hour in range(current_hour + 1):
        hours.append(f"{hour:02d}:00")
        heart_rates.append(0)
        hrvs.append(0)
    
    # Fill in the actual values we have
    for result in heart_rate_results:
        hour = int(result.hour)
        if hour <= current_hour:
            index = hours.index(f"{hour:02d}:00")
            heart_rates[index] = float(result.avg_heart_rate)
    
    for result in hrv_results:
        hour = int(result.hour)
        if hour <= current_hour:
            index = hours.index(f"{hour:02d}:00")
            hrvs[index] = float(result.avg_hrv)
    
    # Process latest values
    latest_heart_rate = 0
    latest_hrv = 0
    latest_timestamp = datetime.utcnow()
    
    for result in latest_results:
        if result.metric_type == 'heart_rate':
            latest_heart_rate = float(result.value)
            latest_timestamp = result.recorded_at
        elif result.metric_type == 'hrv':
            latest_hrv = float(result.value)
    
    # Calculate daily averages for non-zero values
    non_zero_hrs = [hr for hr in heart_rates if hr > 0]
    non_zero_hrvs = [hrv for hrv in hrvs if hrv > 0]
    
    avg_heart_rate = sum(non_zero_hrs) / len(non_zero_hrs) if non_zero_hrs else 0
    avg_hrv = sum(non_zero_hrvs) / len(non_zero_hrvs) if non_zero_hrvs else 0
    
    # Prepare the result
    daily_data = {
        "hourly_averages": {
            "hours": hours,
            "heart_rate": heart_rates,
            "hrv": hrvs
        },
        "latest": {
            "heart_rate": latest_heart_rate,
            "hrv": latest_hrv,
            "timestamp": latest_timestamp.isoformat()
        },
        "daily_average": {
            "heart_rate": avg_heart_rate,
            "hrv": avg_hrv
        }
    }
    
    return daily_data