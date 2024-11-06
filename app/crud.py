from sqlmodel import Session, select
from models.models import User
import uuid
import auth
from schemas.schemas import *

def create_user(db: Session, user: UserCreate):
    if get_user_by_email(db, user.email) is not None:
        return None

    hashed_password = auth.hash_password(user.password)
    db_user = User(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        phone_number=user.phone_number,
        password_hash=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_email(db: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    session_user = db.exec(statement).first()
    if session_user is None:
        return None
    else:
        return session_user

def delete_user(db: Session, user: UserDelete):
    statement = select(User).where(User.email == user.email)
    session_user = db.exec(statement).first()

    verify_password = auth.verify_password(user.password, session_user.password_hash)

    if verify_password is False:
        return False

    db.delete(session_user)
    db.commit()
    return session_user


def update_user(db: Session, user: UserUpdate):
    db_user = get_user_by_email(db, user.current_email)

    if db_user is None:
        return None

    verify_password = auth.verify_password(user.current_password, db_user.password_hash)

    if verify_password is False:
        return False
    
    if user.first_name is not None:
        db_user.first_name = user.first_name
    if user.last_name is not None:
        db_user.last_name = user.last_name
    if user.email is not None:
        db_user.email = user.email
    if user.phone_number is not None:
        db_user.phone_number = user.phone_number
    if user.password is not None:
        db_user.password_hash = auth.hash_password(user.password)

    db.commit()
    db.refresh(db_user)

    return db_user
