import uuid
from datetime import datetime
from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel

class Users(SQLModel, table=True):
    __tablename__ = "users"
    __table_args__ = {"schema": "public"} 

    user_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    first_name: str = Field(max_length=30)
    last_name: str = Field(max_length=30)
    email: str = Field(max_length=100, unique=True)
    phone_number: str = Field(max_length=15)
    password_hash: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

