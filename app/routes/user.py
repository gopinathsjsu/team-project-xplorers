from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import crud, database
from app.schemas import UserSchema

router = APIRouter()

@router.post("/users/", response_model=UserSchema.UserResponse)
def create_user(user: UserSchema.UserCreate, db: Session = Depends(database.get_db)):
    db_user = crud.get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db, user)

@router.get("/users/{user_id}", response_model=UserSchema.UserResponse)
def get_user(user_id: int, db: Session = Depends(database.get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user