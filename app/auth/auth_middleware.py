# filepath: d:\Study\BookTable-App\app\middleware\auth_middleware.py
from fastapi import FastAPI, Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from app.auth.jwt_utils import verify_token

class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI):
        super().__init__(app)
        self.security = HTTPBearer()

    async def dispatch(self, request: Request, call_next):
        if request.url.path in ["/api/login", "/api/register"]:
            response = await call_next(request)
            return response

        credentials: HTTPAuthorizationCredentials = await self.security(request)
        if credentials:
            token = credentials.credentials
            payload = verify_token(token)
            if payload is None:
                raise HTTPException(status_code=401, detail="Invalid or expired token")
            request.state.user = payload
        else:
            raise HTTPException(status_code=403, detail="Not authenticated")

        response = await call_next(request)
        return response