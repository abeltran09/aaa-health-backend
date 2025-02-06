from sqlmodel import Session, select
from models.models import User, AnthropometricMeasurements
from schemas.schemas import *
from datetime import datetime


def handle_websocket_data(
    db: Session, 
    batch: MetricBatch, 
    metric: HealthMetric
    ):
    

