# from enum import 
from sqlalchemy import Column, ForeignKey, Integer, Enum
from app.database import Base
from sqlalchemy.orm import relationship
import enum

class NotificationPreference(enum.Enum):
    EMAIL = "email"
    SMS = "sms"
    BOTH = "both"

class Customer(Base):
    __tablename__ = "customers"

    customer_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, unique=True)
    notification_preference = Column(Enum(NotificationPreference), default=NotificationPreference.EMAIL)

    # Relationships
    user = relationship("User", back_populates="customer")
    # reservations = relationship("Reservation", back_populates="customer")
    # reviews = relationship("Review", back_populates="customer")
