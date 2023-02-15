"""api calls for drones."""
from datetime import datetime, timedelta
from typing import List
from fastapi import Depends, APIRouter, HTTPException, status, UploadFile
from database.drone_updates_table import create_drone_update
from .users import get_current_user
from ..dependencies import drones
from ..dependencies.drones import get_current_drone
from ..dependencies.classes import Drone, DroneEvent, DroneUpdateWithRoute, DroneUpdate, User

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

@router.get("/drones/events/",
            status_code=status.HTTP_200_OK,
            response_model=List[DroneEvent]
            )
async def read_drone_events(drone_id: int=None,
                            zone_id:int =None,
                            days:int =0,
                            hours:int =0,
                            minutes:int =0,
                            current_user: User = Depends(get_current_user)):
    """API call to get all events of a drone

    Args:
        drone_id (int, optional): id of the drone. Defaults to None.
        zone_id (int, optional): zone id. Defaults to None.
        days (int, optional): days before now. Defaults to 0.
        hours (int, optional): hours before now. Defaults to 0.
        minutes (int, optional): minutes before now. Defaults to 0.
        current_user (User, optional): current user that is logged in.
        Defaults to Depends(get_current_user).

    Raises:
        HTTPException: if no events are found.

    Returns:
        _type_: _description_
    """

    timestamp = timestamp_helper(days,hours,minutes)
    drone_events = await drones.get_drone_events(orga_id=current_user.organization.id,
                                           timestamp=timestamp,
                                           drone_id=drone_id,
                                           zone_id=zone_id)
    print(drone_events)
    return drone_events

def timestamp_helper(days:int,hours:int,minutes:int) -> datetime | None:
    """generates a timestamp x days, y hours and z minutes before now.

    Args:
        days (int): number of days.
        hours (int): number of hours.
        minutes (int): number of minutes.

    Returns:
        datetime: the calculated timestamp.
    """
    time_delta = timedelta(days=days,minutes=minutes,hours=hours)
    if time_delta.total_seconds() == 0:
        return None

    return datetime.utcnow() - timedelta

@router.get("/drones/route/",
            status_code=status.HTTP_200_OK,
            response_model=List[DroneUpdateWithRoute]
            )
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

@router.get("/drones/all/",
            status_code=status.HTTP_200_OK,
            response_model=List[Drone])
async def read_drones_all(current_user: User = Depends(get_current_user)):
    """API call to get the all drones

    Args:
        current_user (User, optional): User. Defaults to Depends(get_current_user).

    Returns:
        Drone[]: List of all drones
    """
    return await drones.get_all_drones(current_user.organization.id)

@router.get("/drones/count",
            status_code=status.HTTP_200_OK,
            response_model=int
            )
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

@router.post("/drones/send-update/", status_code=status.HTTP_200_OK)
async def drone_update(update: DroneUpdate, current_drone: Drone = Depends(get_current_drone)):
    """Api call te recieve updates from drones

    Args:
        update (DroneUpdate): updtade object
        current_drone (Drone, optional): drone to use. Defaults to Depends(get_current_drone).

    Returns:
        dict: response
    """
    if current_drone is None:
        return {"message": "invalid drone"}

    create_drone_update(
        current_drone.id,
        update.timestamp,
        update.lon,
        update.lat,
        update.flight_range,
        update.flight_time
    )

    return {"message": "seccess"}


@router.post("/drones/send-event/")
async def drone_event(
    event: DroneEvent,
    file: UploadFile,
    current_drone: Drone = Depends(get_current_drone)):
    """Api call to recieve events form drones

    Args:
        event (DroneEvent): Event from the drone
        file (UploadFile): Associated image file
        current_drone (Drone, optional): Drone to use. Defaults to Depends(get_current_drone).

    Returns:
        dict: response
    """
    #todo: add event to db + create link to saved location (path)
    try:
        if current_drone is None:
            return {"message:": "Invalid drone" }
        content = file.file.read()
        date = str(datetime.now().timestamp())
        new_file_name = file.filename + date
        path = "./drone_images/" + new_file_name + ".jpg"
        new_file = open(path, "w", encoding="utf-8")
        new_file.write(content)
        new_file.close()
        #check if this is correct
        url = "https://kiwa.tech/api/drone_images/" + new_file_name + ".jpg"
        return {"url": url, "event": event}
    except Exception as err:
        print(err)
        return {"message": "success"}
