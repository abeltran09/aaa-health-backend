from fastapi import APIRouter, Depends, Form, HTTPException
import crud
from database import get_db
from models.models import User
from sqlmodel import Session
from typing import Annotated, Optional
from schemas.schemas import *

router = APIRouter()

@router.get("/get-user/", response_model=UserPublic)
def get_user(email: str, db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db=db, email=email)
    if user is None:
        raise HTTPException(status_code=404, detail="User was not found, make sure you typed the email correctly")
    return user

@router.post("/register-user/", response_model=UserPublic)
def create_user(
    first_name: Annotated[str, Form()], 
    last_name: Annotated[str, Form()], 
    email: Annotated[str, Form()], 
    phone_number: Annotated[str, Form()],
    password: Annotated[str, Form()],  
    db: Session = Depends(get_db)
    ):

    user_data = UserCreate(
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone_number=phone_number,
        password=password
    )

    user = crud.create_user(db=db, user=user_data)
    if user is None:
        raise HTTPException(status_code=409, detail="This user email already exists")
    return user

@router.delete("/delete-user/", response_model=UserPublic)
def delete_user(
    email: Annotated[str, Form()],
    password: Annotated[str, Form()],
    db: Session = Depends(get_db)
    ):

    user_data = UserUpdate(
        email=email,
        password=password
    )

    user = crud.delete_user(db=db, user=user_data)

    if user is False:
        raise HTTPException(status_code=401, detail="Incorrect password was entered, make sure you typed correctly")
    return user


@router.put("/update-user-password/", response_model=UserPublic)
def update_user(
    current_email: Annotated[str, Form()],
    current_password: Annotated[str, Form()],
    new_first_name: Annotated[Optional[str], Form()] = None, 
    new_last_name: Annotated[Optional[str], Form()] = None, 
    new_email: Annotated[Optional[str], Form()] = None, 
    new_phone_number: Annotated[Optional[str], Form()] = None,
    new_password: Annotated[Optional[str], Form()] = None, 
    db: Session = Depends(get_db)
    ):

    user_data = UserUpdate(
        current_email=current_email,
        current_password=current_password,
        first_name=new_first_name,
        last_name=new_last_name,
        email=new_email,
        phone_number=new_phone_number,
        password=new_password
    )

    user = crud.update_user(db=db, user=user_data)

    if user is None:
        raise HTTPException(status_code=409, detail="This user email does not exist, make sure you typed correctly")

    if user is False:
        raise HTTPException(status_code=401, detail="Incorrect password was entered, make sure you typed correctly")

    return user
