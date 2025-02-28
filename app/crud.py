from sqlalchemy.orm import Session
from app.models import UserModel
from passlib.context import CryptContext
from app.schemas import UserSchema

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user_by_email(db: Session, email: str):
    return db.query(UserModel.User).filter(UserModel.User.email == email).first()

def create_user(db: Session, user: UserSchema.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = UserModel.User(
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

def get_user(db: Session, user_id: int):
    return db.query(UserModel.User).filter(UserModel.User.user_id == user_id).first()