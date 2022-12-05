from pydantic import BaseModel
from enum import Enum

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None

class Permission(Enum):
    USER = 1
    ADMIN = 2
    THIRD_PARTY = 3

class User(BaseModel):
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None

class UserWithSensitiveInfo(User):
    hashed_password: str
    permission: Permission | None = None
    disabled: bool | None = None
    email_verified: bool