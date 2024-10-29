from typing import Optional
from pydantic import (
    BaseModel,
    EmailStr,
    Field,
)
from datetime import datetime


class SUserView(BaseModel):
    email: EmailStr = Field(...)
    first_name: str = Field(...)
    last_name: str = Field(...)
    gender: str = Field(...)
    avatar: str = Field(...)
    data_create_user: datetime
    distance: Optional[float] = None

    class Config:
        orm_mode = True


