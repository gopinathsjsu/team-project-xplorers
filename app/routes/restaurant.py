from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app import crud, database
from app.schemas import RestaurantSchema
from app.models import RestaurantManagerModel

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

    manager = db.query(RestaurantManagerModel.RestaurantManager).filter(
        RestaurantManagerModel.RestaurantManager.user_id == user["user_id"]
    ).first()
    if not manager:
        raise HTTPException(status_code=404, detail="Manager not found")

    db_restaurant = crud.create_restaurant(db, restaurant, manager_id=manager.manager_id)
    return db_restaurant

@router.get("/manager/restaurants", response_model=list[RestaurantSchema.RestaurantResponse])
async def get_restaurants_by_manager(
    request: Request,
    db: Session = Depends(database.get_db)
):
    user = request.state.user
    if user["role"] != "restaurant_manager":
        raise HTTPException(status_code=403, detail="Not authorized to view these restaurants")
    
    manager = db.query(RestaurantManagerModel.RestaurantManager).filter(
        RestaurantManagerModel.RestaurantManager.user_id == user["user_id"]
    ).first()
    if not manager:
        raise HTTPException(status_code=404, detail="Manager not found")
    
    restaurants = crud.get_restaurants_by_manager(db, manager_id=manager.manager_id)
    return restaurants

@router.get("/admin/restaurants", response_model=list[RestaurantSchema.RestaurantResponse])
async def get_all_restaurants(
    request: Request,
    db: Session = Depends(database.get_db)
):
    user = request.state.user
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to view all restaurants")

    restaurants = crud.get_all_restaurants(db)
    return restaurants