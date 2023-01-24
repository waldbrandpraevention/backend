from fastapi import Depends, APIRouter, FastAPI, HTTPException, status, Request, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from .users import get_current_user
from ..dependencies.drones import get_all_drones, get_drone, get_drone_count
from ..dependencies.classes import User, Drone

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