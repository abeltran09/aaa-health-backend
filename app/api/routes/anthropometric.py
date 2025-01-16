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

@router.post("/adding-anthropometrics/")
def get_weight(
    weight: Annotated[str, Form()],
    height: Annotated[str, Form()],
    email: Annotated[str, Form()],
    db: Session = Depends(get_db())
    ):

    user_id = crud.get_user_id(db=db, email)

    if user_id is None:
        return "error getting user_id"

    measurment_data = Measurments(
        user_id=user_id,
        weight=weight,
        height=height
    )

    anthropometric = crud.add_anthropometrics(db=db, measurments=measurment_data)

    if anthropometric == "Successful":
        return

    return "Measurements Entered were went wrong"


    



