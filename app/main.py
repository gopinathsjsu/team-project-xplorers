from fastapi import FastAPI
from app.auth.auth_middleware import AuthMiddleware
from app.routes import user, restaurant

app = FastAPI(title="FastAPI Backend")
app.add_middleware(AuthMiddleware)

app.include_router(user.router, prefix="/api", tags=["Users"])
app.include_router(restaurant.router, prefix="/api")
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
