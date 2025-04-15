from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm

# from app.auth.auth_middleware import AuthMiddleware
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app import crud_restaurants, database
from app.auth.jwt_utils import create_access_token
from app.schemas import UserSchema

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter()


@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(database.get_db),
):
    user = crud_restaurants.get_user_by_email(db, form_data.username)
    if not user or not pwd_context.verify(form_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    access_token = create_access_token(
        data={"user_id": user.user_id, "email": user.email, "role": user.role.value}
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", response_model=UserSchema.UserResponse)
def create_user(user: UserSchema.UserCreate, db: Session = Depends(database.get_db)):
    db_user = crud_restaurants.get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud_restaurants.create_user(db, user)


@router.get("/users/{user_id}", response_model=UserSchema.UserResponse)
def get_user(user_id: int, db: Session = Depends(database.get_db)):
    db_user = crud_restaurants.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.get("/protected-route")
async def protected_route(request: Request):
    user = request.state.user
    return {"message": f"Hello, {user['email']} with role {user['role']}"}
