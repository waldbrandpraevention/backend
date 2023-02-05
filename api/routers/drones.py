"""api calls for drones."""
import datetime
from typing import List
from fastapi import Depends, APIRouter, HTTPException, status
from .users import get_current_user
from ..dependencies import drones
from ..dependencies.classes import Drone, DroneEvent, DroneUpdateWithRoute, User

router = APIRouter()


@router.get("/drones/", status_code=status.HTTP_200_OK, response_model=Drone)
async def read_drone(drone_id: int, current_user: User = Depends(get_current_user)):
    """API call to get a specific drone

    Args:
        name (str): Name of the drone
        current_user (User, optional): User. Defaults to Depends(get_current_user).

    Returns:
        Drone: drone
    """

    drone = await drones.get_drone(drone_id,current_user.organization.id)
    if drone is None:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Drone does not exist.",
        )
    return drone

@router.get("/drones/events/", status_code=status.HTTP_200_OK, response_model=List[DroneEvent])
async def read_drone_events(drone_id: int=None,
                            zone_id:int =None,
                            days:int =0,
                            hours:int =0,
                            minutes:int =0,
                            current_user: User = Depends(get_current_user)):
    #TODO
    """_summary_

    Args:
        drone_id (int, optional): _description_. Defaults to None.
        zone_id (int, optional): _description_. Defaults to None.
        days (int, optional): _description_. Defaults to 0.
        hours (int, optional): _description_. Defaults to 0.
        minutes (int, optional): _description_. Defaults to 0.
        current_user (User, optional): _description_. Defaults to Depends(get_current_user).

    Raises:
        HTTPException: _description_

    Returns:
        _type_: _description_
    """

    timestamp = timestamp_helper(days,hours,minutes)
    drone_events = await drones.get_drone_events(orga_id=current_user.organization.id,
                                           timestamp=timestamp,
                                           drone_id=drone_id,
                                           zone_id=zone_id)
    if drone_events is None:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Couldnt find any events.",
        )
    
    return drone_events

def timestamp_helper(days:int,hours:int,minutes:int) -> datetime.datetime | None:
    """generates a timestamp x days, y hours and z minutes before now.

    Args:
        days (int): number of days.
        hours (int): number of hours.
        minutes (int): number of minutes.

    Returns:
        datetime: the calculated timestamp.
    """
    timedelta = datetime.timedelta(days=days,minutes=minutes,hours=hours)
    if timedelta.total_seconds() == 0:
        return None

    return datetime.datetime.utcnow() - timedelta

@router.get("/drones/route", status_code=status.HTTP_200_OK, response_model=List[DroneUpdateWithRoute])
async def read_drone_route( drone_id: int=None,
                            zone_id:int =None,
                            days:int =0,
                            hours:int =0,
                            minutes:int =0,
                            current_user: User = Depends(get_current_user)):
    """API call to get a specific drone

    Args:
        name (str): Name of the drone
        current_user (User, optional): User. Defaults to Depends(get_current_user).

    Returns:
        Drone: drone
    """

    timestamp = timestamp_helper(days,hours,minutes)
    drone_events = await drones.get_drone_with_route(orga_id=current_user.organization.id,
                                           timestamp=timestamp,
                                           drone_id=drone_id,
                                           zone_id=zone_id)
    if drone_events is None:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Couldnt find any updates.",
        )

    return drone_events

@router.get("/drones/all/", status_code=status.HTTP_200_OK)
async def read_drones_all(current_user: User = Depends(get_current_user)):
    """API call to get the all drones

    Args:
        current_user (User, optional): User. Defaults to Depends(get_current_user).

    Returns:
        Drone[]: List of all drones
    """
    return await drones.get_all_drones(current_user.organization.id)

@router.get("/drones/count", status_code=status.HTTP_200_OK)
async def read_drones_count(
                            zone_id: int,
                            current_user: User = Depends(get_current_user)
                            ):
    """API call to get the amount of drones in a zone

    Args:
        current_user (User, optional): User. Defaults to Depends(get_current_user).

    Returns:
        int: Amount of drones
    """
    return await drones.get_drone_count(zone_id,current_user.organization.id)
