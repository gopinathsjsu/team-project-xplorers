import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from fastapi import status, FastAPI

# Import the main app and components
from app.main import app, verify_token, custom_openapi


@pytest.fixture
def client():
    """
    Create a test client for the FastAPI application.
    """
    return TestClient(app)


@pytest.fixture
def mock_auth_middleware():
    """
    Mock the AuthMiddleware to avoid actual authentication in tests.
    """
    with patch("app.auth.auth_middleware.AuthMiddleware") as mock:
        yield mock


def test_app_initialization():
    """
    Test that the FastAPI app is initialized correctly.
    """
    assert app.title == "FastAPI Backend"
    assert app.docs_url == "/docs"


def test_cors_middleware():
    """
    Test CORS middleware configuration.
    """
    # Extract CORS middleware from app middleware stack
    cors_middleware = None
    for middleware in app.user_middleware:
        if middleware.cls.__name__ == "CORSMiddleware":
            cors_middleware = middleware
            break
    
    assert cors_middleware is not None
    assert "http://localhost:3000" in cors_middleware.options["allow_origins"]
    assert "http://127.0.0.1:3000" in cors_middleware.options["allow_origins"]
    assert cors_middleware.options["allow_credentials"] is True
    assert "GET" in cors_middleware.options["allow_methods"]
    assert "POST" in cors_middleware.options["allow_methods"]
    assert "PUT" in cors_middleware.options["allow_methods"]
    assert "DELETE" in cors_middleware.options["allow_methods"]
    assert "OPTIONS" in cors_middleware.options["allow_methods"]
    assert "PATCH" in cors_middleware.options["allow_methods"]


def test_auth_middleware_added():
    """
    Test that the AuthMiddleware is added to the app.
    """
    # Check if AuthMiddleware is in the middleware stack
    auth_middleware_exists = any(
        middleware.cls.__name__ == "AuthMiddleware" 
        for middleware in app.user_middleware
    )
    assert auth_middleware_exists


def test_open_endpoint(client):
    """
    Test that the open endpoint is accessible without authentication.
    """
    response = client.get("/open")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"msg": "everybody can see this"}


def test_protected_endpoint_no_token(client):
    """
    Test that the protected endpoint returns 401 when no token is provided.
    """
    response = client.get("/protected")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    # Assert that the response contains WWW-Authenticate header
    assert "WWW-Authenticate" in response.headers


def test_protected_endpoint_invalid_token(client):
    """
    Test that the protected endpoint returns 401 when an invalid token is provided.
    """
    response = client.get("/protected", headers={"Authorization": "Bearer invalid-token"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_protected_endpoint_valid_token(client):
    """
    Test that the protected endpoint works with a valid token.
    """
    # The verify_token function in main.py accepts "foo" as a valid token
    response = client.get("/protected", headers={"Authorization": "Bearer foo"})
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"msg": "this is protected", "user": {"sub": "user_id"}}


def test_verify_token():
    """
    Test the verify_token function directly.
    """
    mock_credentials = MagicMock()
    mock_credentials.credentials = "foo"
    
    # Should return user info for valid token
    result = verify_token(mock_credentials)
    assert result == {"sub": "user_id"}
    
    # Should raise exception for invalid token
    mock_credentials.credentials = "invalid"
    with pytest.raises(Exception) as excinfo:
        verify_token(mock_credentials)
    assert "Invalid token" in str(excinfo.value)


def test_custom_openapi():
    """
    Test that the custom OpenAPI schema is correctly generated.
    """
    # Clear any cached schema
    app.openapi_schema = None
    
    # Get the schema
    schema = custom_openapi()
    
    # Check security scheme is added
    assert "securitySchemes" in schema["components"]
    assert "BearerAuth" in schema["components"]["securitySchemes"]
    assert schema["components"]["securitySchemes"]["BearerAuth"]["type"] == "http"
    assert schema["components"]["securitySchemes"]["BearerAuth"]["scheme"] == "bearer"
    assert schema["components"]["securitySchemes"]["BearerAuth"]["bearerFormat"] == "JWT"
    
    # Check global security requirement is added
    assert "security" in schema
    assert {"BearerAuth": []} in schema["security"]


def test_routers_included():
    """
    Test that all routers are included with the correct prefixes and tags.
    """
    router_paths = {route.tags[0]: route.path for route in app.routes if hasattr(route, 'tags') and route.tags}
    
    # Check for existence of routes with specific tags
    assert any(tag == ["Users"] for route in app.routes if hasattr(route, 'tags') and route.tags)
    assert any(tag == ["Restaurants"] for route in app.routes if hasattr(route, 'tags') and route.tags)
    assert any(tag == ["Operating Hours"] for route in app.routes if hasattr(route, 'tags') and route.tags)
    assert any(tag == ["Tables"] for route in app.routes if hasattr(route, 'tags') and route.tags)
    assert any(tag == ["Reservation Slots"] for route in app.routes if hasattr(route, 'tags') and route.tags)
    assert any(tag == ["Customer Reviews"] for route in app.routes if hasattr(route, 'tags') and route.tags)
    assert any(tag == ["Reservations"] for route in app.routes if hasattr(route, 'tags') and route.tags)
    assert any(tag == ["Photos"] for route in app.routes if hasattr(route, 'tags') and route.tags)
    
    # Check that all routes with tags start with /api
    api_routes = [route for route in app.routes if hasattr(route, 'tags') and route.tags and route.tags[0] in [
        "Users", "Restaurants", "Operating Hours", "Tables", 
        "Reservation Slots", "Customer Reviews", "Reservations", "Photos"
    ]]
    
    for route in api_routes:
        assert route.path.startswith("/api")


def test_openapi_endpoint(client):
    """
    Test that the OpenAPI schema endpoint returns the expected data.
    """
    response = client.get("/openapi.json")
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["info"]["title"] == "FastAPI Backend"
    assert "components" in data
    assert "securitySchemes" in data["components"]
    assert "BearerAuth" in data["components"]["securitySchemes"]


def test_docs_endpoint(client):
    """
    Test that the docs endpoint is accessible.
    """
    response = client.get("/docs")
    assert response.status_code == status.HTTP_200_OK
    assert "text/html" in response.headers["content-type"]


# Test different HTTP methods against protected endpoint
@pytest.mark.parametrize("method", ["get", "post", "put", "delete", "patch"])
def test_protected_endpoint_http_methods(client, method):
    """
    Test that different HTTP methods work on protected endpoints with authentication.
    """
    # Skip OPTIONS since it's handled differently in CORS
    if method == "options":
        return
        
    request_method = getattr(client, method)
    response = request_method("/protected", headers={"Authorization": "Bearer foo"})
    
    if method == "get":
        # GET should succeed
        assert response.status_code == status.HTTP_200_OK
    else:
        # Other methods should either succeed or return 405 Method Not Allowed
        # but should NOT return authentication errors
        assert response.status_code != status.HTTP_401_UNAUTHORIZED
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_405_METHOD_NOT_ALLOWED]