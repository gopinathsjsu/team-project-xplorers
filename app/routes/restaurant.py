# filepath: d:\Study\BookTable-App\app\routes\restaurant.py
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app import crud, database
from app.schemas import RestaurantSchema
from app.auth.auth_middleware import AuthMiddleware

router = APIRouter()

@router.post("/manager/restaurants", response_model=RestaurantSchema.RestaurantResponse)
async def create_restaurant(
    restaurant: RestaurantSchema.RestaurantCreate,
    request: Request,
    db: Session = Depends(database.get_db)
):
    user = request.state.user
    if user["role"] != "restaurant_manager":
        raise HTTPException(status_code=403, detail="Not authorized to create a restaurant")

    db_restaurant = crud.create_restaurant(db, restaurant, manager_id=user["user_id"])
    return db_restaurant