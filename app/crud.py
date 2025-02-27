from sqlalchemy.orm import Session
from app.models import userModel, userSchema
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user_by_email(db: Session, email: str):
    return db.query(userModel.User).filter(userModel.User.email == email).first()

def create_user(db: Session, user: userSchema.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = userModel.User(
        email=user.email,
        password_hash=hashed_password,
        phone_number=user.phone_number,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# def create_user(db: Session, user: userSchema.UserCreate):
#     hashed_password = pwd_context.hash(user.password)
#     db_user = userModel.User(username=user.username, email=user.email, hashed_password=hashed_password)
#     db.add(db_user)
#     db.commit()
#     db.refresh(db_user)
#     return db_user