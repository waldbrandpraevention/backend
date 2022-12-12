
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
    organization: str | None = None

class UserWithSensitiveInfo(User):
    hashed_password: str | None = None
    permission: Permission | None = None
    disabled: bool | None = None
    email_verified: bool

class FireRisk(Enum):
    VERY_LOW = 1
    LOW = 2
    MIDDLE = 3
    HEIGH = 4
    VERY_HEIGH = 5


class Zone(BaseModel):
    name: str | None = None
    fire_risk: FireRisk | None = None