from pydantic import (
    BaseModel,
    EmailStr,
    Field,
)


class SUserView(BaseModel):
    email: EmailStr = Field(...)
    first_name: str = Field(...)
    last_name: str = Field(...)
    gender: str = Field(...)
    avatar: str = Field(...)


