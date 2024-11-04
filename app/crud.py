from sqlmodel import Session, select
from models.models import User
import uuid

# CREATE a new user
def create_user(db: Session, user: User):
    db_user = User(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        phone_number=user.phone_number,
        password_hash=user.password_hash
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

