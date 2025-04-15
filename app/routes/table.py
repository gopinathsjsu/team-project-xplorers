from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app import database
from app.models import RestaurantManagerModel, RestaurantModel, TableModel
from app.schemas import TableSchema

router = APIRouter()


# Manager routes for table management
@router.post(
    "/manager/restaurants/{restaurant_id}/tables",
    response_model=TableSchema.TableResponse,
    status_code=201,
)
async def add_table(
    restaurant_id: int,
    table: TableSchema.TableCreate,
    request: Request,
    db: Session = Depends(database.get_db),
):
    user = request.state.user
    if user["role"] != "restaurant_manager":
        raise HTTPException(
            status_code=403, detail="Not authorized to add tables to this restaurant"
        )

    # Verify that the restaurant exists and is managed by the current manager
    restaurant = (
        db.query(RestaurantModel.Restaurant)
        .join(RestaurantManagerModel.RestaurantManager)
        .filter(
            RestaurantModel.Restaurant.restaurant_id == restaurant_id,
            RestaurantManagerModel.RestaurantManager.user_id == user["user_id"],
        )
        .first()
    )
    if not restaurant:
        raise HTTPException(
            status_code=404, detail="Restaurant not found or not managed by you"
        )

    # Create the new table inline (replacing create_table helper)
    new_table = TableModel.Table(
        capacity=table.capacity,
        table_number=table.table_number,
        is_active=table.is_active,
        restaurant_id=restaurant_id,
    )
    db.add(new_table)
    db.commit()
    db.refresh(new_table)
    return new_table


@router.get(
    "/manager/restaurants/{restaurant_id}/tables",
    response_model=list[TableSchema.TableResponse],
)
async def get_tables(
    restaurant_id: int, request: Request, db: Session = Depends(database.get_db)
):
    user = request.state.user
    if user["role"] != "restaurant_manager":
        raise HTTPException(
            status_code=403, detail="Not authorized to view tables for this restaurant"
        )

    # Verify that the restaurant exists and is managed by the current manager
    restaurant = (
        db.query(RestaurantModel.Restaurant)
        .join(RestaurantManagerModel.RestaurantManager)
        .filter(
            RestaurantModel.Restaurant.restaurant_id == restaurant_id,
            RestaurantManagerModel.RestaurantManager.user_id == user["user_id"],
        )
        .first()
    )
    if not restaurant:
        raise HTTPException(
            status_code=404, detail="Restaurant not found or not managed by you"
        )

    # Retrieve all tables for the restaurant (in place of get_tables_by_restaurant)
    tables = (
        db.query(TableModel.Table)
        .filter(TableModel.Table.restaurant_id == restaurant_id)
        .all()
    )
    return tables


@router.put(
    "/manager/restaurants/{restaurant_id}/tables/{table_id}",
    response_model=TableSchema.TableResponse,
)
async def update_table(
    restaurant_id: int,
    table_id: int,
    table_update: TableSchema.TableUpdate,
    request: Request,
    db: Session = Depends(database.get_db),
):
    user = request.state.user
    if user["role"] != "restaurant_manager":
        raise HTTPException(
            status_code=403,
            detail="Not authorized to update tables for this restaurant",
        )

    # Verify that the restaurant exists and is managed by the current manager
    restaurant = (
        db.query(RestaurantModel.Restaurant)
        .join(RestaurantManagerModel.RestaurantManager)
        .filter(
            RestaurantModel.Restaurant.restaurant_id == restaurant_id,
            RestaurantManagerModel.RestaurantManager.user_id == user["user_id"],
        )
        .first()
    )
    if not restaurant:
        raise HTTPException(
            status_code=404, detail="Restaurant not found or not managed by you"
        )

    # Retrieve the table by table_id and restaurant_id (inlining get_table_by_id_and_restaurant)
    table = (
        db.query(TableModel.Table)
        .filter(
            TableModel.Table.table_id == table_id,
            TableModel.Table.restaurant_id == restaurant_id,
        )
        .first()
    )
    if not table:
        raise HTTPException(
            status_code=404,
            detail="Table not found or does not belong to this restaurant",
        )

    # Update table fields inline (replacing update_table_db)
    for key, value in table_update.dict(exclude_unset=True).items():
        setattr(table, key, value)
    db.commit()
    db.refresh(table)
    return table


@router.delete(
    "/manager/restaurants/{restaurant_id}/tables/{table_id}", status_code=204
)
async def delete_table(
    restaurant_id: int,
    table_id: int,
    request: Request,
    db: Session = Depends(database.get_db),
):
    user = request.state.user
    if user["role"] != "restaurant_manager":
        raise HTTPException(
            status_code=403,
            detail="Not authorized to delete tables for this restaurant",
        )

    # Verify that the restaurant exists and is managed by the current manager
    restaurant = (
        db.query(RestaurantModel.Restaurant)
        .join(RestaurantManagerModel.RestaurantManager)
        .filter(
            RestaurantModel.Restaurant.restaurant_id == restaurant_id,
            RestaurantManagerModel.RestaurantManager.user_id == user["user_id"],
        )
        .first()
    )
    if not restaurant:
        raise HTTPException(
            status_code=404, detail="Restaurant not found or not managed by you"
        )

    # Retrieve the table by table_id and restaurant_id (in place of get_table_by_id_and_restaurant)
    table = (
        db.query(TableModel.Table)
        .filter(
            TableModel.Table.table_id == table_id,
            TableModel.Table.restaurant_id == restaurant_id,
        )
        .first()
    )
    if not table:
        raise HTTPException(
            status_code=404,
            detail="Table not found or does not belong to this restaurant",
        )

    # Delete the table inline (replacing delete_table_db)
    db.delete(table)
    db.commit()
    return {"detail": "Table deleted successfully"}
