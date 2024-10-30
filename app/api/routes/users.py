from fastapi import APIRouter, Depends
import crud
from database import get_db
from models.user import Users
from sqlmodel import Session

router = APIRouter()

@router.post("/users/", response_model=Users)
def create_user(user: Users, db: Session = Depends(get_db)):
    return crud.create_user(db=db, user=user)