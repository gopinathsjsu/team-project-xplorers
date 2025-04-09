from datetime import time
from pydantic import BaseModel, validator

from app.schemas.RestaurantSchema import DayOfWeek


class OperatingHoursCreate(BaseModel):
    day_of_week: DayOfWeek
    opening_time: time
    closing_time: time

    @validator('closing_time')
    def closing_after_opening(cls, v, values):
        if 'opening_time' in values and v <= values['opening_time']:
            raise ValueError('closing_time must be after opening_time')
        return v