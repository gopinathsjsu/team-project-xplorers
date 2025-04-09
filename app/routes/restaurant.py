from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app import crud_restaurants, database
from app.schemas import RestaurantSchema
from app.models import RestaurantManagerModel

router = APIRouter()

# Manager routes for restaurant management
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

    db_restaurant = crud_restaurants.create_restaurant(db, restaurant, manager_id=manager.manager_id)
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
    
    restaurants = crud_restaurants.get_restaurants_by_manager(db, manager_id=manager.manager_id)
    return restaurants

@router.get("/manager/restaurants/{restaurant_id}", response_model=RestaurantSchema.RestaurantDetailResponse)
async def get_restaurant_details(
    restaurant_id: int,
    request: Request,
    db: Session = Depends(database.get_db)
):
    user = request.state.user
    if user["role"] != "restaurant_manager":
        raise HTTPException(status_code=403, detail="Not authorized to view this restaurant")

    restaurant = crud_restaurants.get_restaurant_by_id_and_manager(db, restaurant_id, user["user_id"])
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found or not managed by you")

    return restaurant

@router.put("/manager/restaurants/{restaurant_id}", response_model=RestaurantSchema.RestaurantResponse)
async def update_restaurant_details(
    restaurant_id: int,
    restaurant_update: RestaurantSchema.RestaurantUpdate,
    request: Request,
    db: Session = Depends(database.get_db)
):
    user = request.state.user
    if user["role"] != "restaurant_manager":
        raise HTTPException(status_code=403, detail="Not authorized to update this restaurant")

    restaurant = crud_restaurants.get_restaurant_by_id_and_manager(db, restaurant_id, user["user_id"])
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found or not managed by you")

    # Update the restaurant details
    updated_restaurant = crud_restaurants.update_restaurant(db, restaurant_id, restaurant_update)
    return updated_restaurant

@router.delete("/manager/restaurants/{restaurant_id}", status_code=204)
async def delete_restaurant(
    restaurant_id: int,
    request: Request,
    db: Session = Depends(database.get_db)
):
    user = request.state.user
    if user["role"] != "restaurant_manager":
        raise HTTPException(status_code=403, detail="Not authorized to delete this restaurant")

    restaurant = crud_restaurants.get_restaurant_by_id_and_manager(db, restaurant_id, user["user_id"])
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found or not managed by you")

    # Mark the restaurant as inactive
    crud_restaurants.delete_restaurant_manager(db, restaurant_id)
    return {"detail": "Restaurant deleted successfully"}

# Admin routes for restaurant management
@router.get("/admin/restaurants", response_model=list[RestaurantSchema.RestaurantResponse])
async def get_all_restaurants(
    request: Request,
    db: Session = Depends(database.get_db)
):
    user = request.state.user
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to view all restaurants")

    restaurants = crud_restaurants.get_all_restaurants(db)
    return restaurants

@router.delete("/admin/restaurants/{restaurant_id}", status_code=204)
async def delete_restaurant(
    restaurant_id: int,
    request: Request,
    db: Session = Depends(database.get_db)
):
    user = request.state.user
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to delete a restaurant")

    # Check if the restaurant exists
    restaurant = crud_restaurants.get_restaurant_by_id(db, restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    # Delete the restaurant
    crud_restaurants.delete_restaurant(db, restaurant_id)
    return {"detail": "Restaurant deleted successfully"}