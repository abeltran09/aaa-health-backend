import uuid
from datetime import datetime
from sqlmodel import Field, Relationship, SQLModel
from typing import Optional, List

class User(SQLModel, table=True):
    user_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    first_name: str = Field(max_length=30)
    last_name: str = Field(max_length=30)
    email: str = Field(max_length=100, unique=True)
    phone_number: str = Field(max_length=15)
    password_hash: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship with AnthropometricMeasurements
    anthropometric_measurements: Optional["AnthropometricMeasurements"] = Relationship(back_populates="user")
    metric_batch: List["MetricBatch"] = Relationship(back_populates="user")

class AnthropometricMeasurments(SQLModel, table=True):
    anthropometric_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.user_id", unique=True, nullable=False)
    height: str = Field(max_length=5)
    weight: str = Field(max_length=3)
    sex: str = Field(max_length=6)

    # Relationship with Users
    user: Optional[User] = Relationship(back_populates="anthropometric_measurements")

class MetricBatch(SQLModel, table=True):
    batch_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.user_id", nullable=False)
    recorded_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship with User
    user: Optional[User] = Relationship(back_populates="metric_batch")
    health_metrics: List["HealthMetrics"] = Relationship(back_populates="metric_batch")

class HealthMetrics(SQLModel, table=True):
    metric_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    batch_id: uuid.UUID = Field(foreign_key="metricbatch.batch_id", nullable=False)
    metric_type: str = Field(max_length=20)
    value: float = Field()
    unit: str = Field(max_length=10)

    # Relationship with MetricBatch
    metric_batch: Optional[MetricBatch] = Relationship(back_populates="health_metrics")