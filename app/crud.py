from sqlmodel import Session, select
from models.models import User
import uuid
import auth
from schemas.schemas import *
from datetime import datetime

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

def delete_user(db: Session, user: UserAuth):
    statement = select(User).where(User.email == user.email)
    session_user = db.exec(statement).first()

    verify_password = auth.verify_password(user.password, session_user.password_hash)

    if verify_password is False:
        return False

    db.delete(session_user)
    db.commit()
    return session_user


def update_password(db: Session, user: UserUpdate):
    db_user = get_user_by_email(db, user.current_email)

    if db_user is None:
        return False

    verify_password = auth.verify_password(user.current_password, db_user.password_hash)

    if verify_password is False:
        return False

    confirm_passwords = auth.confirm_matching_passwords(user.new_password, user.confirm_new_password)

    if confirm_passwords is False:
        return False
    
    
    db_user.password_hash = auth.hash_password(user.new_password)

    db_user.updated_at = user.updated_at

    db.commit()
    db.refresh(db_user)

    return db_user

def edit_profile(db: Session, user: EditProfile):
    db_user = get_user_by_email(db, user.old_email)

    if db_user is None:
        return None
    
    if user.first_name is not None:
        db_user.first_name = user.first_name
    if user.last_name is not None:
        db_user.last_name = user.last_name
    if user.email is not None:
        db_user.email = user.email
    if user.phone_number is not None:
        db_user.phone_number = user.phone_number

    db_user.updated_at = user.updated_at

    db.commit()
    db.refresh(db_user)

    return db_user
