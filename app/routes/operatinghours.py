from datetime import time
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Path, Request, logger
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import RestaurantModel
from app.models.OperatingHoursModel import OperatingHours
from app.schemas import RestaurantSchema
from app.schemas.OperatingHoursSchema import OperatingHoursCreate

# Define the router
router = APIRouter()


def check_timeframes(start_1: time, end_1: time, start_2: time, end_2: time) -> bool:
    if start_1 is None and end_1 is None:
        return True
    # They overlap if the start of one interval is before the end of the other and vice versa.
    return end_1 <= start_2 or end_2 <= start_1


@router.post(
    "/manager/restaurants/{restaurant_id}/hours",
    response_model=RestaurantSchema.OperatingHoursResponse,
)
async def create_operating_hours(
    restaurant_id: int,
    operating_hours: OperatingHoursCreate,
    request: Request,
    db: Session = Depends(get_db),
):
    # Verify that the user is authorized to perform this action.
    user = request.state.user
    if user["role"] != "restaurant_manager":
        raise HTTPException(
            status_code=403, detail="Not authorized to create operating hours"
        )

    # Verify that the restaurant exists.
    restaurant = (
        db.query(RestaurantModel.Restaurant)
        .filter(RestaurantModel.Restaurant.restaurant_id == restaurant_id)
        .first()
    )
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    existing_hours = (
        db.query(OperatingHours)
        .filter(
            OperatingHours.restaurant_id == restaurant_id,
            OperatingHours.day_of_week == operating_hours.day_of_week,
        )
        .first()
    )
    # Check if the new operating hours conflict with existing ones for the same day of the week.
    if existing_hours and existing_hours.day_of_week == operating_hours.day_of_week:
        if not check_timeframes(
            operating_hours.opening_time,
            operating_hours.closing_time,
            existing_hours.opening_time,
            existing_hours.closing_time,
        ):
            raise HTTPException(
                status_code=400,
                detail="Operating hours conflict: the specified time frame overlaps with an existing schedule for this day.",
            )

    # Create new operating hours record.
    new_operating_hours = OperatingHours(
        day_of_week=operating_hours.day_of_week,
        opening_time=operating_hours.opening_time,
        closing_time=operating_hours.closing_time,
        restaurant_id=restaurant_id,  # Use restaurant_id from the path
    )
    db.add(new_operating_hours)
    db.commit()
    db.refresh(new_operating_hours)
    if not new_operating_hours:
        raise HTTPException(status_code=400, detail="Failed to create operating hours")

    return new_operating_hours


@router.get(
    "/manager/restaurants/{restaurant_id}/hours",
    response_model=List[RestaurantSchema.OperatingHoursResponse],
)
async def get_operating_hours(
    restaurant_id: int, request: Request, db: Session = Depends(get_db)
):
    # Verify that the user is authorized to perform this action.
    user = request.state.user
    if user["role"] != "restaurant_manager":
        raise HTTPException(
            status_code=403, detail="Not authorized to view operating hours"
        )

    # Verify that the restaurant exists.
    restaurant = (
        db.query(RestaurantModel.Restaurant)
        .filter(RestaurantModel.Restaurant.restaurant_id == restaurant_id)
        .first()
    )
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    # Fetch operating hours for the given restaurant ID
    operating_hours = (
        db.query(OperatingHours)
        .filter(OperatingHours.restaurant_id == restaurant_id)
        .all()
    )
    if not operating_hours:
        raise HTTPException(
            status_code=404, detail="No operating hours found for this restaurant"
        )

    return operating_hours


@router.put(
    "/manager/restaurants/{restaurant_id}/hours/{hours_id}",
    response_model=RestaurantSchema.OperatingHoursResponse,
)
async def update_operating_hours(
    restaurant_id: int = Path(..., title="The ID of the restaurant", ge=1),
    hours_id: int = Path(..., title="The ID of the operating hours entry", ge=1),
    operating_hours: OperatingHoursCreate = None,
    request: Request = None,
    db: Session = Depends(get_db),
):
    # Verify that the user is authorized to perform this action.
    user = request.state.user
    if user["role"] != "restaurant_manager":
        raise HTTPException(
            status_code=403, detail="Not authorized to update operating hours"
        )

    # Verify that the restaurant exists.
    restaurant = (
        db.query(RestaurantModel.Restaurant)
        .filter(RestaurantModel.Restaurant.restaurant_id == restaurant_id)
        .first()
    )
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    # Fetch the operating hours record to be updated.
    existing_record = (
        db.query(OperatingHours)
        .filter(
            OperatingHours.hours_id == hours_id,
            OperatingHours.restaurant_id == restaurant_id,
        )
        .first()
    )
    if not existing_record:
        raise HTTPException(status_code=404, detail="Operating hours not found")

    # Check for any conflicting operating hours on the same day.
    # We exclude the record being updated.
    conflicting_record = (
        db.query(OperatingHours)
        .filter(
            OperatingHours.restaurant_id == restaurant_id,
            OperatingHours.day_of_week == operating_hours.day_of_week,
            OperatingHours.hours_id != hours_id,
        )
        .first()
    )

    if conflicting_record:
        if not check_timeframes(
            operating_hours.opening_time,
            operating_hours.closing_time,
            conflicting_record.opening_time,
            conflicting_record.closing_time,
        ):
            raise HTTPException(
                status_code=400,
                detail="Operating hours conflict: the specified time frame overlaps with an existing schedule for this day.",
            )

    # Update the fields in the existing record.
    existing_record.day_of_week = operating_hours.day_of_week
    existing_record.opening_time = operating_hours.opening_time
    existing_record.closing_time = operating_hours.closing_time

    # Commit the changes and refresh the instance.
    db.commit()
    db.refresh(existing_record)

    return existing_record


@router.delete(
    "/manager/restaurants/{restaurant_id}/hours/{hours_id}", response_model=dict
)
async def delete_operating_hours(
    restaurant_id: int, hours_id: int, request: Request, db: Session = Depends(get_db)
):
    # Verify that the user is authorized to perform this action.
    user = request.state.user
    if user["role"] != "restaurant_manager":
        raise HTTPException(
            status_code=403, detail="Not authorized to delete operating hours"
        )

    # Verify that the restaurant exists.
    restaurant = (
        db.query(RestaurantModel.Restaurant)
        .filter(RestaurantModel.Restaurant.restaurant_id == restaurant_id)
        .first()
    )
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    # Fetch the existing operating hours record
    operating_hours = (
        db.query(OperatingHours)
        .filter(
            OperatingHours.hours_id == hours_id,
            OperatingHours.restaurant_id == restaurant_id,
        )
        .first()
    )
    if not operating_hours:
        raise HTTPException(status_code=404, detail="Operating hours not found")

    # Delete the record
    db.delete(operating_hours)
    db.commit()
    return {"message": "Operating hours deleted successfully"}
