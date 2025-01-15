from fastapi import APIRouter, Depends, Form, HTTPException
import crud
from database import get_db
from models.models import User
from sqlmodel import Session
from typing import Annotated, Optional
from schemas.schemas import *
import auth
from datetime import datetime

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

@router.post("/login-user/", response_model=UserPublic)
def login_user(
    email: Annotated[str, Form()],
    password: Annotated[str, Form()],
    db: Session = Depends(get_db)
    ):

    user_data = UserAuth(
        email=email,
        password=password
    )

    user = auth.login(db, user_data)

    if user is None:
        raise HTTPException(status_code=401, detail="Incorrect email or password was entered, make sure you typed correctly")
    return user



@router.delete("/delete-user/", response_model=UserPublic)
def delete_user(
    email: Annotated[str, Form()],
    password: Annotated[str, Form()],
    db: Session = Depends(get_db)
    ):

    user_data = UserAuth(
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
    old_password: Annotated[str, Form()],
    new_password: Annotated[str, Form()],
    confirm_new_password: Annotated[str, Form()],
    updated_at: datetime = datetime.utcnow(),
    db: Session = Depends(get_db)
    ):

    user_data = UserUpdate(
        current_email=current_email,
        current_password=old_password,
        new_password=new_password,
        confirm_new_password=confirm_new_password,
        updated_at=updated_at
    )

    user = crud.update_password(db=db, user=user_data)

    if user is False:
        raise HTTPException(status_code=401, detail="Incorrect password was entered, make sure you typed correctly")

    return user

@router.put("/edit-profile/", response_model=UserPublic)
def edit_user_profile(
    current_email: Annotated[str, Form()],
    updated_at: datetime = datetime.utcnow(),
    new_first_name: Annotated[Optional[str], Form()] = None, 
    new_last_name: Annotated[Optional[str], Form()] = None, 
    new_email: Annotated[Optional[str], Form()] = None, 
    new_phone_number: Annotated[Optional[str], Form()] = None,
    db: Session = Depends(get_db)
    ):

    user_data = EditProfile(
        first_name=new_first_name,
        last_name=new_last_name,
        email=new_email,
        phone_number=new_phone_number,
        old_email=current_email,
        updated_at=updated_at
    )

    user = crud.edit_profile(db=db, user=user_data)

    return user