import re
from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator


class UserRegisterScheme(BaseModel):
    id: Optional[int] = None
    username: str
    email: EmailStr
    first_name: Optional[str] = ""
    last_name: Optional[str] = ""
    password: str

    @field_validator("password", mode='before')
    @classmethod
    def validate_password(cls, value):
        return value
        password = value
        min_length = 8
        if len(password) < min_length:
            raise ValueError('Password must be at least 8 characters long.')
        if not any(character.islower() for character in password):
            raise ValueError('Password should contain at least one lowercase character.')
        return value

class UserScheme(BaseModel):
    id: Optional[int] = None
    username: str
    email: EmailStr
    first_name: Optional[str] = ""
    last_name: Optional[str] = ""
    is_email_verified: bool = False


class ExtendedUserScheme(UserScheme):
    hashed_password: str


class AdminUserScheme(ExtendedUserScheme):
    is_superuser: bool


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


class TokenScheme(BaseModel):
    refresh_token: str
    access_token: str

    @field_validator("refresh_token", 'access_token', mode="before")
    @classmethod
    def validate_token(cls, value):
        pattern = r"^[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+\.[A-Za-z0-9-_]*$"
        if re.match(pattern, value):
            return value
        else:
            raise ValueError("Not valid refresh token")
