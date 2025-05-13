import pytest # type: ignore
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app


# Create an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """
    Create a clean database session for a test.
    
    We create the database tables once for all tests and then drop and recreate
    data between tests to ensure isolation.
    """
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Clean up tables after each test
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """
    Create a FastAPI TestClient with the test database.
    """
    # Override the get_db dependency to use our test database
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
        
    # Remove the override after the test is complete
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_user(client):
    """
    Create a test user for authentication tests.
    """
    user_data = {
        "email": "test@example.com",
        "password": "password123",
        "full_name": "Test User"
    }
    response = client.post("/api/users/", json=user_data)
    assert response.status_code == 201
    return response.json()


@pytest.fixture(scope="function")
def auth_headers(client, test_user):
    """
    Get authentication headers for the test user.
    """
    login_data = {
        "username": test_user["email"],
        "password": "password123"
    }
    response = client.post("/api/token", data=login_data)
    assert response.status_code == 200
    
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}