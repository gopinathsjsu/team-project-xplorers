from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import crud, database
from app.models import userSchema

router = APIRouter()

@router.post("/users/", response_model=userSchema.UserResponse)
def create_user(user: userSchema.UserCreate, db: Session = Depends(database.get_db)):
    db_user = crud.get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db, user)

# @router.post("/users/", response_model=userSchema.UserResponse)
# def create_user(user: userSchema.UserCreate, db: Session = Depends(database.get_db)):
#     db_user = crud.get_user_by_email(db, user.email)
#     if db_user:
#         raise HTTPException(status_code=400, detail="Email already registered")
#     return crud.create_user(db, user)
