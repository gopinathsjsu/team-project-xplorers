from fastapi import FastAPI

from app.auth.auth_middleware import AuthMiddleware
from app.routes import operatinghours, reservationslots, restaurant, user

app = FastAPI(
    title="FastAPI Backend",
    docs_url="/docs",
)
app.add_middleware(AuthMiddleware)

app.include_router(user.router, prefix="/api", tags=["Users"])
app.include_router(restaurant.router, prefix="/api")
app.include_router(operatinghours.router, prefix="/api", tags=["Operating Hours"])
app.include_router(reservationslots.router, prefix="/api", tags=["Reservation Slots"])
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
