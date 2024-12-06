import bcrypt
import crud

# Function to hash a password
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed_password.decode("utf-8")

# Function to verify a password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

def login(db, user_data):
    user = crud.get_user_by_email(db=db, email=user_data.email)
    if verify_password(user_data.password, user.password_hash):
        return user
    return None