from fastapi import APIRouter, Depends, Form, HTTPException
import crud
from database import get_db
from models.models import User
from sqlmodel import Session
from typing import Annotated, Optional
from schemas.schemas import *
import auth
from datetime import datetime
from dotenv import load_dotenv
import os
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone


oauth2_bearer = OAuth2PasswordBearer(tokenUrl='/users/login-user/')

router = APIRouter()

async def get_current_user(
    token: Annotated[str, Depends(oauth2_bearer)], 
    db: Session = Depends(get_db)
    ) -> User:
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = crud.get_user_by_email(db=db, email=email)
    if user is None:
        raise HTTPException(status_code=404, detail="User was not found, make sure you typed the email correctly")
    return user


@router.get("/get-user/", response_model=UserPublic)
def get_user(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db)
    ) -> User:

    return current_user
    

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

@router.post("/login-user/")
def login_user(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db)
    ):

    user = auth.login(db, UserAuth(email=form_data.username, password=form_data.password))

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=30)
    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}



@router.delete("/delete-user/", response_model=UserPublic)
async def delete_user(
    current_user: Annotated[User, Depends(get_current_user)],
    password: Annotated[str, Form()],
    db: Session = Depends(get_db)
    ):

    user_data = UserAuth(
        email=current_user.email,
        password=password
    )

    user = crud.delete_user(db=db, user=user_data)
    if user is False:
        raise HTTPException(status_code=401, detail="Incorrect password")
    return user


@router.put("/update-user-password/", response_model=PasswordUpdateResponse)
async def update_user(
    current_user: Annotated[User, Depends(get_current_user)],
    old_password: Annotated[str, Form()],
    new_password: Annotated[str, Form()],
    confirm_new_password: Annotated[str, Form()],
    db: Session = Depends(get_db)
):
    user_data = UserUpdate(
        current_email=current_user.email,
        current_password=old_password,
        new_password=new_password,
        confirm_new_password=confirm_new_password,
        updated_at=datetime.utcnow()
    )

    result = crud.update_password(db=db, user=user_data)
    if isinstance(result, PasswordUpdateError):
        return PasswordUpdateResponse(success=False, error=result)
    
    return PasswordUpdateResponse(success=True, user=result)

@router.put("/edit-profile/", response_model=UserPublic)
async def edit_user_profile(
    current_user: Annotated[User, Depends(get_current_user)],
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
        old_email=current_user.email,
        updated_at=datetime.utcnow()
    )

    user = crud.edit_profile(db=db, user=user_data)
    return user