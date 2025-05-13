import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from datetime import datetime, time
from app.main import app
from app.models import (
    CustomerModel,
    ReservationModel,
    RestaurantManagerModel,
    RestaurantModel,
    TableModel,
    ReservationSlotModel
)

client = TestClient(app)

@pytest.fixture
def mock_db_session():
    return MagicMock()

@pytest.fixture
def mock_customer():
    return CustomerModel.Customer(
        customer_id=1,
        user_id=1,
        first_name="John",
        last_name="Doe",
        email="john@example.com"
    )

@pytest.fixture
def mock_restaurant():
    return RestaurantModel.Restaurant(
        restaurant_id=1,
        name="Test Restaurant",
        address_line1="123 Test St",
        city="Test City",
        state="TS",
        zip_code="12345",
        phone_number="123-456-7890"
    )

@pytest.fixture
def mock_table():
    return TableModel.Table(
        table_id=1,
        restaurant_id=1,
        capacity=4,
        is_active=True
    )

@pytest.fixture
def mock_reservation():
    return ReservationModel.Reservation(
        reservation_id=1,
        customer_id=1,
        restaurant_id=1,
        table_id=1,
        reservation_time=datetime(2024, 3, 20, 19, 0),
        party_size=4,
        status=ReservationModel.ReservationStatus.CONFIRMED,
        confirmation_code="ABC123",
        special_requests="Window seat"
    )

@pytest.fixture
def mock_reservation_slot():
    return ReservationSlotModel.ReservationSlot(
        slot_id=1,
        restaurant_id=1,
        slot_time=datetime(2024, 3, 20, 19, 0),
        available_tables=5,
        is_active=True
    )

@pytest.fixture
def mock_customer_user():
    return {
        "user_id": 1,
        "role": "customer",
        "email": "john@example.com",
        "first_name": "John"
    }

@pytest.fixture
def mock_manager_user():
    return {
        "user_id": 1,
        "role": "restaurant_manager"
    }

@patch('app.routes.reservation.get_db')
def test_book_table_success(mock_get_db, mock_db_session, mock_customer, mock_table, mock_restaurant, mock_customer_user):
    # Configure mocks
    mock_get_db.return_value = mock_db_session
    mock_db_session.query.return_value.filter.return_value.first.side_effect = [
        mock_customer,  # For customer query
        mock_table,     # For table query
        mock_restaurant # For restaurant query
    ]

    # Test data
    reservation_data = {
        "restaurant_id": 1,
        "table_id": 1,
        "reservation_time": "2024-03-20T19:00:00",
        "party_size": 4,
        "special_requests": "Window seat"
    }

    # Mock request state
    client.app.dependency_overrides[lambda: mock_customer_user] = lambda: mock_customer_user

    # Test the endpoint
    response = client.post("/reservations", json=reservation_data)

    # Assertions
    assert response.status_code == 201
    assert "confirmation_code" in response.json()
    assert response.json()["restaurant_name"] == "Test Restaurant"

@patch('app.routes.reservation.get_db')
def test_book_table_unauthorized(mock_get_db, mock_db_session, mock_manager_user):
    # Configure mocks
    mock_get_db.return_value = mock_db_session

    # Test data
    reservation_data = {
        "restaurant_id": 1,
        "table_id": 1,
        "reservation_time": "2024-03-20T19:00:00",
        "party_size": 4
    }

    # Mock request state
    client.app.dependency_overrides[lambda: mock_manager_user] = lambda: mock_manager_user

    # Test the endpoint
    response = client.post("/reservations", json=reservation_data)

    # Assertions
    assert response.status_code == 403
    assert response.json() == {"detail": "Not authorized to book reservations"}

@patch('app.routes.reservation.get_db')
def test_get_availability_success(mock_get_db, mock_db_session, mock_restaurant, mock_reservation_slot, mock_customer_user):
    # Configure mocks
    mock_get_db.return_value = mock_db_session
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_restaurant
    mock_db_session.query.return_value.filter.return_value.all.return_value = [mock_reservation_slot]

    # Mock request state
    client.app.dependency_overrides[lambda: mock_customer_user] = lambda: mock_customer_user

    # Test the endpoint
    response = client.get("/restaurants/1/availability")

    # Assertions
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["restaurant_id"] == 1

@patch('app.routes.reservation.get_db')
def test_list_reservations_success(mock_get_db, mock_db_session, mock_customer, mock_reservation, mock_restaurant, mock_customer_user):
    # Configure mocks
    mock_get_db.return_value = mock_db_session
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_customer
    mock_db_session.query.return_value.join.return_value.filter.return_value.order_by.return_value.all.return_value = [
        (mock_reservation, mock_restaurant.name)
    ]

    # Mock request state
    client.app.dependency_overrides[lambda: mock_customer_user] = lambda: mock_customer_user

    # Test the endpoint
    response = client.get("/reservations")

    # Assertions
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["restaurant_name"] == "Test Restaurant"

@patch('app.routes.reservation.get_db')
def test_update_reservation_success(mock_get_db, mock_db_session, mock_customer, mock_reservation, mock_table, mock_reservation_slot, mock_customer_user):
    # Configure mocks
    mock_get_db.return_value = mock_db_session
    mock_db_session.query.return_value.filter.return_value.first.side_effect = [
        mock_customer,
        mock_reservation,
        mock_table,
        mock_reservation_slot
    ]

    # Test data
    update_data = {
        "party_size": 6,
        "special_requests": "Updated request"
    }

    # Mock request state
    client.app.dependency_overrides[lambda: mock_customer_user] = lambda: mock_customer_user

    # Test the endpoint
    response = client.put("/reservations/1", json=update_data)

    # Assertions
    assert response.status_code == 200
    assert response.json()["party_size"] == 6
    assert response.json()["special_requests"] == "Updated request"

@patch('app.routes.reservation.get_db')
def test_cancel_reservation_success(mock_get_db, mock_db_session, mock_customer, mock_reservation, mock_table, mock_customer_user):
    # Configure mocks
    mock_get_db.return_value = mock_db_session
    mock_db_session.query.return_value.filter.return_value.first.side_effect = [
        mock_customer,
        mock_reservation,
        mock_table
    ]

    # Mock request state
    client.app.dependency_overrides[lambda: mock_customer_user] = lambda: mock_customer_user

    # Test the endpoint
    response = client.delete("/reservations/1")

    # Assertions
    assert response.status_code == 204

@patch('app.routes.reservation.get_db')
def test_list_all_reservations_manager_success(mock_get_db, mock_db_session, mock_restaurant, mock_reservation, mock_manager_user):
    # Configure mocks
    mock_get_db.return_value = mock_db_session
    mock_db_session.query.return_value.join.return_value.filter.return_value.first.return_value = mock_restaurant
    mock_db_session.query.return_value.filter.return_value.order_by.return_value.all.return_value = [mock_reservation]

    # Mock request state
    client.app.dependency_overrides[lambda: mock_manager_user] = lambda: mock_manager_user

    # Test the endpoint
    response = client.get("/manager/restaurants/1/reservations")

    # Assertions
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["reservation_id"] == 1 