from fastapi import APIRouter, Depends
import crud
from database import get_db
from models.models import User
from sqlmodel import Session

router = APIRouter()

@router.post("/users/", response_model=User)
def create_user(user: User, db: Session = Depends(get_db)):
    return crud.create_user(db=db, user=user)