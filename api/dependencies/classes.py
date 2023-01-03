
import datetime
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

class Setting(BaseModel):
    id: int|None =None
    name: str|None =None
    description: str|None =None
    default_value: int|None =None

class User(BaseModel):
    id: int | None = None
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    organization_id: int | None = None

class Organization(BaseModel):
    id: int | None = None
    name: str | None = None
    abbreviation: str | None = None

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

class Drone(BaseModel):
    id: int | None = None
    name: str | None = None
    droneowner_id: int | None = None

class DroneData(BaseModel):
    drone_id :int | None = None
    timestamp :datetime.datetime | None = None
    longitude :float | None = None
    latitude :float | None = None
    picture_path :str| None = None
    ai_predictions :dict| None = None
    csv_file_path :str| None = None