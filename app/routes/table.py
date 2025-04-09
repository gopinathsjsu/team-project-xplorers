from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app import crud, database
from app.schemas import TableSchema

router = APIRouter()

# Manager routes for table management
@router.post("/manager/restaurants/{restaurant_id}/tables", response_model=TableSchema.TableResponse, status_code=201)
async def add_table(
    restaurant_id: int,
    table: TableSchema.TableCreate,
    request: Request,
    db: Session = Depends(database.get_db)
):
    user = request.state.user
    if user["role"] != "restaurant_manager":
        raise HTTPException(status_code=403, detail="Not authorized to add tables to this restaurant")

    # Check if the restaurant exists and is managed by the current manager
    restaurant = crud.get_restaurant_by_id_and_manager(db, restaurant_id, user["user_id"])
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found or not managed by you")

    # Add the new table
    new_table = crud.create_table(db, table, restaurant_id)
    return new_table

@router.get("/manager/restaurants/{restaurant_id}/tables", response_model=list[TableSchema.TableResponse])
async def get_tables(
    restaurant_id: int,
    request: Request,
    db: Session = Depends(database.get_db)
):
    user = request.state.user
    if user["role"] != "restaurant_manager":
        raise HTTPException(status_code=403, detail="Not authorized to view tables for this restaurant")

    # Check if the restaurant exists and is managed by the current manager
    restaurant = crud.get_restaurant_by_id_and_manager(db, restaurant_id, user["user_id"])
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found or not managed by you")

    # Retrieve all tables for the restaurant
    tables = crud.get_tables_by_restaurant(db, restaurant_id)
    return tables

@router.put("/manager/restaurants/{restaurant_id}/tables/{table_id}", response_model=TableSchema.TableResponse)
async def update_table(
    restaurant_id: int,
    table_id: int,
    table_update: TableSchema.TableUpdate,
    request: Request,
    db: Session = Depends(database.get_db)
):
    user = request.state.user
    if user["role"] != "restaurant_manager":
        raise HTTPException(status_code=403, detail="Not authorized to update tables for this restaurant")

    # Check if the restaurant exists and is managed by the current manager
    restaurant = crud.get_restaurant_by_id_and_manager(db, restaurant_id, user["user_id"])
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found or not managed by you")

    # Check if the table exists and belongs to the restaurant
    table = crud.get_table_by_id_and_restaurant(db, table_id, restaurant_id)
    if not table:
        raise HTTPException(status_code=404, detail="Table not found or does not belong to this restaurant")

    # Update the table details
    updated_table = crud.update_table(db, table_id, table_update)
    return updated_table

@router.delete("/manager/restaurants/{restaurant_id}/tables/{table_id}", status_code=204)
async def delete_table(
    restaurant_id: int,
    table_id: int,
    request: Request,
    db: Session = Depends(database.get_db)
):
    user = request.state.user
    if user["role"] != "restaurant_manager":
        raise HTTPException(status_code=403, detail="Not authorized to delete tables for this restaurant")

    # Check if the restaurant exists and is managed by the current manager
    restaurant = crud.get_restaurant_by_id_and_manager(db, restaurant_id, user["user_id"])
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found or not managed by you")

    # Check if the table exists and belongs to the restaurant
    table = crud.get_table_by_id_and_restaurant(db, table_id, restaurant_id)
    if not table:
        raise HTTPException(status_code=404, detail="Table not found or does not belong to this restaurant")

    # Delete or deactivate the table
    crud.delete_table(db, table_id)
    return {"detail": "Table deleted successfully"}


def create_table(db: Session, table: TableSchema.TableCreate, restaurant_id: int):
    new_table = TableModel.Table(
        capacity=table.capacity,
        table_number=table.table_number,
        is_active=table.is_active,
        restaurant_id=restaurant_id
    )
    db.add(new_table)
    db.commit()
    db.refresh(new_table)
    return new_table

def get_tables_by_restaurant(db: Session, restaurant_id: int):
    return db.query(TableModel.Table).filter(TableModel.Table.restaurant_id == restaurant_id).all()

from app.models import TableModel

def get_table_by_id_and_restaurant(db: Session, table_id: int, restaurant_id: int):
    return db.query(TableModel.Table).filter(
        TableModel.Table.table_id == table_id,
        TableModel.Table.restaurant_id == restaurant_id
    ).first()

def update_table(db: Session, table_id: int, table_update: TableSchema.TableUpdate):
    table = db.query(TableModel.Table).filter(TableModel.Table.table_id == table_id).first()
    if not table:
        return None

    for key, value in table_update.dict(exclude_unset=True).items():
        setattr(table, key, value)

    db.commit()
    db.refresh(table)
    return table

def delete_table(db: Session, table_id: int):
    table = db.query(TableModel.Table).filter(TableModel.Table.table_id == table_id).first()
    if table:
        db.delete(table)
        db.commit()