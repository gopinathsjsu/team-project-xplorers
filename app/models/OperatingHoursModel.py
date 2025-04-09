from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, Time
from app.database import Base
from sqlalchemy.orm import relationship

from app.schemas.RestaurantSchema import DayOfWeek

class OperatingHours(Base):
    __tablename__ = "operating_hours"

    hours_id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.restaurant_id"), nullable=False)
    day_of_week = Column(Enum(DayOfWeek), nullable=False)
    opening_time = Column(Time, nullable=False)
    closing_time = Column(Time, nullable=False)

    # Relationships
    restaurants = relationship("Restaurant", back_populates="operating_hours")