
import datetime
from typing import List
from pydantic import BaseModel
from enum import Enum
from datetime import datetime

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None

class Permission(Enum):
    USER = 1
    ADMIN = 2
    THIRD_PARTY = 3

class SettingsType(int,Enum):
    INTEGER=0
    STRING =1
    JSON =2

class Setting(BaseModel):
    id: int|None =None
    name: str|None =None
    description: str|None =None
    default_value: str|int|dict|None =None
    type: SettingsType|None=None

class UserSetting(BaseModel):
    id: int|None =None
    user_id: int|None=None
    name: str|None =None
    description: str|None =None
    value: str|int|dict|None=None
    type: SettingsType|None=None

class Organization(BaseModel):
    id: int | None = None
    name: str | None = None
    abbreviation: str | None = None

class User(BaseModel):
    id: int | None = None
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    organization: Organization | None = None
    permission: Permission | None = None
    disabled: bool | None = None
    email_verified: bool

class UserWithSensitiveInfo(User):
    hashed_password: str | None = None

class FireRisk(Enum):
    VERY_LOW = 1
    LOW = 2
    MIDDLE = 3
    HEIGH = 4
    VERY_HEIGH = 5

class Allert(BaseModel):
    content: str | None = None
    date: datetime | None = None

class Drone(BaseModel):
    """ name: name of the aerial vehicle according to manufacturer,
        type: type of the aerial vehicle,
        flight_range: maximum flight range of the aerial vehicle in [km],
        cc_range: maximum command and control range of the aerial vehicle in [km],
        flight_time: maximum flight time of the aerial vehicle in [minutes],
        last_update: timestamp of last communication with drone.
        ?zone: zone the drone is currently in."""
    id: int | None = None
    name: str | None = None
    type: str | None = None
    flight_range: float | None = None
    cc_range: float | None = None
    flight_time: float | None = None
    last_update: datetime | None = None
    zone: str | None = None
    droneowner_id: int | None = None

class DroneUpdate(BaseModel):
    drone_id :int | None = None
    timestamp :datetime | None = None
    longitude :float | None = None
    latitude :float | None = None
    flight_range: float | None = None
    flight_time: float | None = None

class EventType(Enum):
    SMOKE = 1
    FIRE = 2

class DroneEvent(BaseModel):
    drone_id :int | None = None
    timestamp :datetime | None = None
    longitude :float | None = None
    latitude :float | None = None
    event_type: EventType | None = None
    confidence: int | None = None
    picture_path :str| None = None
    ai_predictions :dict| None = None
    csv_file_path :str| None = None

class Zone(BaseModel):
    id: int | None = None
    name: str | None = None
    federal_state: str | None = None
    district: str | None = None
    events: List[DroneEvent] | None = None
    fire_risk: FireRisk | None = None
    ai: FireRisk | None = None
    coordinates: List[List[List[List[float]]]] | None = None
