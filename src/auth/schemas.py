import re
from typing import Optional

from pydantic import BaseModel, field_validator


class UserRegisterScheme(BaseModel):
    id: Optional[int] = None
    username: str
    email: str
    first_name: Optional[str] = ""
    last_name: Optional[str] = ""
    password: str


class UserScheme(BaseModel):
    id: Optional[int] = None
    username: str
    email: str
    first_name: Optional[str] = ""
    last_name: Optional[str] = ""


class ExtendedUserScheme(UserScheme):
    hashed_password: str


class UserLoginData(BaseModel):
    email: str
    password: str


class TokenPayload(BaseModel):
    subject: str
    expire: int


class RefreshToken(BaseModel):
    refresh_token: str

    @field_validator("refresh_token", mode="before")
    @classmethod
    def validate_token(cls, value):
        pattern = r"^[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+\.[A-Za-z0-9-_]*$"
        if re.match(pattern, value):
            return value
        else:
            raise ValueError("Not valid refresh token")