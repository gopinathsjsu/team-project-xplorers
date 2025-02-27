from fastapi import FastAPI
from app.routes import user

app = FastAPI(title="FastAPI Backend Boilerplate123")

app.include_router(user.router, prefix="/api", tags=["Users"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
