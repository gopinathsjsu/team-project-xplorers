from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, time
from enum import Enum

class UserRole(str, Enum):
    CUSTOMER = "customer"
    RESTAURANT_MANAGER = "restaurant_manager"
    ADMIN = "admin"

class UserBase(BaseModel):
    email: EmailStr
    phone_number: Optional[str] = None
    first_name: str
    last_name: str
    role: UserRole

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[UserRole] = None

class UserResponse(UserBase):
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# class UserCreate(BaseModel):
#     username: str
#     email: EmailStr
#     password: str

# class UserResponse(BaseModel):
#     id: int
#     username: str
#     email: str

#     class Config:
#         orm_mode = True
