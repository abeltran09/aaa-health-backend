from sqlmodel import Session, select
from models.models import MetricBatch, HealthMetrics
from datetime import datetime

# def handle_websocket_data(
#     db: Session, 
#     batch: MetricBatch, 
#     metric: HealthMetric,
#     user_id: uuid.UUID
#     ):
    
#     batch_data = MetricBatch(
#         user_id=user_id,
#         datetime.utcnow()
#     )

#     metric_data = HealthMetrics(
#         batch_id=batch_data.id,
#         metric
#     )

