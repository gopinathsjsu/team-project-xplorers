import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from datetime import time
from app.main import app
from app.models import RestaurantModel
from app.models.OperatingHoursModel import OperatingHours
from app.routes.operatinghours import check_timeframes

client = TestClient(app)

@pytest.fixture
def mock_db_session():
    return MagicMock()

@pytest.fixture
def mock_restaurant():
    return RestaurantModel.Restaurant(
        restaurant_id=1,
        name="Test Restaurant",
        address_line1="123 Test St",
        city="Test City",
        state="TS",
        zip_code="12345"
    )

@pytest.fixture
def mock_operating_hours():
    return OperatingHours(
        hours_id=1,
        restaurant_id=1,
        day_of_week="Monday",
        opening_time=time(9, 0),  # 9:00 AM
        closing_time=time(22, 0)  # 10:00 PM
    )

@pytest.fixture
def mock_user():
    return {
        "user_id": 1,
        "role": "restaurant_manager"
    }

def test_check_timeframes():
    # Test non-overlapping timeframes
    assert check_timeframes(
        time(9, 0), time(17, 0),  # 9 AM - 5 PM
        time(18, 0), time(22, 0)  # 6 PM - 10 PM
    ) is True

    # Test overlapping timeframes
    assert check_timeframes(
        time(9, 0), time(17, 0),  # 9 AM - 5 PM
        time(16, 0), time(20, 0)  # 4 PM - 8 PM
    ) is False

    # Test None values
    assert check_timeframes(None, None, time(9, 0), time(17, 0)) is True

@patch('app.routes.operatinghours.get_db')
def test_create_operating_hours_success(mock_get_db, mock_db_session, mock_restaurant, mock_user):
    # Configure mocks
    mock_get_db.return_value = mock_db_session
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_restaurant
    
    # Test data
    operating_hours_data = {
        "operating_hours": [
            {
                "day_of_week": "Monday",
                "opening_time": "09:00:00",
                "closing_time": "22:00:00"
            }
        ]
    }

    # Mock request state
    client.app.dependency_overrides[lambda: mock_user] = lambda: mock_user

    # Test the endpoint
    response = client.post(
        "/manager/restaurants/1/hours",
        json=operating_hours_data
    )

    # Assertions
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["day_of_week"] == "Monday"

@patch('app.routes.operatinghours.get_db')
def test_create_operating_hours_unauthorized(mock_get_db, mock_db_session, mock_user):
    # Configure mocks
    mock_get_db.return_value = mock_db_session
    mock_user["role"] = "customer"  # Change role to unauthorized

    # Test data
    operating_hours_data = {
        "operating_hours": [
            {
                "day_of_week": "Monday",
                "opening_time": "09:00:00",
                "closing_time": "22:00:00"
            }
        ]
    }

    # Mock request state
    client.app.dependency_overrides[lambda: mock_user] = lambda: mock_user

    # Test the endpoint
    response = client.post(
        "/manager/restaurants/1/hours",
        json=operating_hours_data
    )

    # Assertions
    assert response.status_code == 403
    assert response.json() == {"detail": "Not authorized to create operating hours"}

@patch('app.routes.operatinghours.get_db')
def test_get_operating_hours_success(mock_get_db, mock_db_session, mock_restaurant, mock_operating_hours, mock_user):
    # Configure mocks
    mock_get_db.return_value = mock_db_session
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_restaurant
    mock_db_session.query.return_value.filter.return_value.all.return_value = [mock_operating_hours]

    # Mock request state
    client.app.dependency_overrides[lambda: mock_user] = lambda: mock_user

    # Test the endpoint
    response = client.get("/manager/restaurants/1/hours")

    # Assertions
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["day_of_week"] == "Monday"

@patch('app.routes.operatinghours.get_db')
def test_update_operating_hours_success(mock_get_db, mock_db_session, mock_restaurant, mock_operating_hours, mock_user):
    # Configure mocks
    mock_get_db.return_value = mock_db_session
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_restaurant
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_operating_hours

    # Test data
    operating_hours_data = {
        "operating_hours": [
            {
                "day_of_week": "Monday",
                "opening_time": "10:00:00",
                "closing_time": "23:00:00"
            }
        ]
    }

    # Mock request state
    client.app.dependency_overrides[lambda: mock_user] = lambda: mock_user

    # Test the endpoint
    response = client.put(
        "/manager/restaurants/1/hours",
        json=operating_hours_data
    )

    # Assertions
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["day_of_week"] == "Monday"

@patch('app.routes.operatinghours.get_db')
def test_delete_operating_hours_success(mock_get_db, mock_db_session, mock_restaurant, mock_operating_hours, mock_user):
    # Configure mocks
    mock_get_db.return_value = mock_db_session
    mock_db_session.query.return_value.filter.return_value.first.side_effect = [mock_restaurant, mock_operating_hours]

    # Mock request state
    client.app.dependency_overrides[lambda: mock_user] = lambda: mock_user

    # Test the endpoint
    response = client.delete("/manager/restaurants/1/hours/1")

    # Assertions
    assert response.status_code == 200
    assert response.json() == {"message": "Operating hours deleted successfully"}

@patch('app.routes.operatinghours.get_db')
def test_delete_operating_hours_not_found(mock_get_db, mock_db_session, mock_restaurant, mock_user):
    # Configure mocks
    mock_get_db.return_value = mock_db_session
    mock_db_session.query.return_value.filter.return_value.first.side_effect = [mock_restaurant, None]

    # Mock request state
    client.app.dependency_overrides[lambda: mock_user] = lambda: mock_user

    # Test the endpoint
    response = client.delete("/manager/restaurants/1/hours/999")

    # Assertions
    assert response.status_code == 404
    assert response.json() == {"detail": "Operating hours not found"} 