from fastapi import Depends, APIRouter, FastAPI, HTTPException, status, Request, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from .users import get_current_user
from ..dependencies.drones import get_all_drones, get_drone, get_drone_count
from ..dependencies.classes import User, Drone
from ..dependencies.authentication import create_access_token, DRONE_TOKEN_EXPIRE_WEEKS
from datetime import datetime, timedelta

router = APIRouter()


@router.get("/drones/", status_code=status.HTTP_200_OK)
async def read_drone(name: str, current_user: User = Depends(get_current_user)):
    """API call to get a specific drone

    Args:
        name (str): Name of the drone
        current_user (User, optional): User. Defaults to Depends(get_current_user).

    Returns:
        Drone: drone
    """

    drone = get_drone(name)
    if drone == None:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Drone does not exist ",
        )
    return drone

@router.get("/drones/all/", status_code=status.HTTP_200_OK)
async def read_drones_all(current_user: User = Depends(get_current_user)):
    """API call to get the all drones

    Args:
        current_user (User, optional): User. Defaults to Depends(get_current_user).

    Returns:
        Drone[]: List of all drones
    """
    return await get_all_drones()

@router.get("/drones/count/", status_code=status.HTTP_200_OK)
async def read_drones_count(current_user: User = Depends(get_current_user)):
    """API call to get the amount of drones

    Args:
        current_user (User, optional): User. Defaults to Depends(get_current_user).

    Returns:
        int: Amount of drones
    """
    return await get_drone_count()

@router.post("/drones/login/", status_code=status.HTTP_200_OK)
async def drone_login(
    name: str | None = None
    type: str | None = None
    flight_range: float | None = None
    cc_range: float | None = None
    flight_time: float | None = None
    last_update: datetime | None = None
    zone: str | None = None
    droneowner_id: int | None = None):
    """API call to create a new drone

    Args:
        todo

    Returns:
        str: token
    """

     if len(name) == 0:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Drone name must be at least one chacter long",
        )
    
    #create new drone in db that gets deleted when the token expires
    #use get_drone(name) to check if already exists, if yes than keep it and just return a new token

    access_token_expires = timedelta(weeks=DRONE_TOKEN_EXPIRE_WEEKS)
    access_token = create_access_token(
        data={"sub": drone.name}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}