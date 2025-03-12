from pydantic import BaseModel
from typing import Optional, Union
from datetime import datetime
import uuid
from enum import Enum
from models.models import User

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone_number: str
    password: str

class UserPublic(BaseModel):
    user_id: uuid.UUID
    first_name: str
    last_name: str
    email: str
    phone_number: str

class UserAuth(BaseModel):
    email: str
    password: str

class UserUpdate(BaseModel):
    current_email: str
    current_password: str
    new_password: str
    confirm_new_password: str
    updated_at: datetime

class UserLogin(BaseModel):
    first_name: str
    last_name: str

class EditProfile(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    old_email: str
    updated_at: datetime

class Measurements(BaseModel):
    user_id: uuid.UUID
    weight: str
    height: str

class Token(BaseModel):
    access_token: str
    token_type: str

class PasswordUpdateError(str, Enum):
    INCORRECT_PASSWORD = "incorrect_old_password"
    PASSWORDS_DONT_MATCH = "passwords_dont_match"
    USER_NOT_FOUND = "user_not_found"

class PasswordUpdateResponse(BaseModel):
    success: bool
    error: Optional[PasswordUpdateError] = None
    user: Optional[UserPublic] = None

class MetricBatch(BaseModel):
    user_id: uuid.UUID
    recorded_at: datetime

class HealthMetric(BaseModel):
    batch_id: uuid.UUID
    metric_type: str
    value: float
    unit: str

class UserIdRequest(BaseModel):
    user_id: str