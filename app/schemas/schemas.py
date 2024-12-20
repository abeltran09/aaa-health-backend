from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone_number: str
    password: str

class UserPublic(BaseModel):
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
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    password: Optional[str] = None

class UserLogin(BaseModel):
    first_name: str
    last_name: str