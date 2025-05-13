import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from datetime import datetime
from app.main import app
from app.models import UserModel, RestaurantModel, ReservationModel
from app.routes.email import send_email_notification

client = TestClient(app)

@pytest.fixture
def mock_db_session():
    return MagicMock()

@pytest.fixture
def mock_reservation():
    return ReservationModel.Reservation(
        reservation_id=1,
        reservation_time=datetime(2024, 3, 20, 19, 0),
        party_size=4,
        confirmation_code="ABC123",
        special_requests="Window seat",
        customer=UserModel.User(
            user_id=1,
            email="test@example.com",
            first_name="John",
            customer=UserModel.Customer()
        ),
        restaurant=RestaurantModel.Restaurant(
            restaurant_id=1,
            name="Test Restaurant",
            address_line1="123 Test St",
            city="Test City",
            state="TS",
            zip_code="12345",
            phone_number="123-456-7890"
        )
    )

def test_send_email_notification_success():
    with patch('smtplib.SMTP') as mock_smtp:
        # Configure mock
        mock_smtp_instance = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_smtp_instance

        # Test the function
        result = send_email_notification(
            to_email="test@example.com",
            subject="Test Subject",
            body="Test Body"
        )

        # Assertions
        assert result is True
        mock_smtp_instance.starttls.assert_called_once()
        mock_smtp_instance.login.assert_called_once()
        mock_smtp_instance.send_message.assert_called_once()

def test_send_email_notification_failure():
    with patch('smtplib.SMTP') as mock_smtp:
        # Configure mock to raise an exception
        mock_smtp.side_effect = Exception("SMTP Error")

        # Test the function
        result = send_email_notification(
            to_email="test@example.com",
            subject="Test Subject",
            body="Test Body"
        )

        # Assertions
        assert result is False

@patch('app.routes.email.send_email_notification')
def test_send_booking_confirmation_success(mock_send_email, mock_db_session, mock_reservation):
    # Configure mock
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_reservation
    mock_send_email.return_value = True

    # Test the endpoint
    response = client.post(f"/send-booking-confirmation/{mock_reservation.reservation_id}")

    # Assertions
    assert response.status_code == 200
    assert response.json() == {"message": "Booking confirmation email sent successfully"}
    mock_send_email.assert_called_once()

@patch('app.routes.email.send_email_notification')
def test_send_booking_confirmation_reservation_not_found(mock_send_email, mock_db_session):
    # Configure mock to return None (reservation not found)
    mock_db_session.query.return_value.filter.return_value.first.return_value = None

    # Test the endpoint
    response = client.post("/send-booking-confirmation/999")

    # Assertions
    assert response.status_code == 404
    assert response.json() == {"detail": "Reservation not found"}
    mock_send_email.assert_not_called()

@patch('app.routes.email.send_email_notification')
def test_send_booking_confirmation_email_failure(mock_send_email, mock_db_session, mock_reservation):
    # Configure mocks
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_reservation
    mock_send_email.return_value = False

    # Test the endpoint
    response = client.post(f"/send-booking-confirmation/{mock_reservation.reservation_id}")

    # Assertions
    assert response.status_code == 500
    assert response.json() == {"detail": "Failed to send email"}
    mock_send_email.assert_called_once() 