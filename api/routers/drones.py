"""api calls for drones."""
import os
from datetime import datetime, timedelta
from typing import List
from fastapi import Depends, APIRouter, HTTPException, status, UploadFile, File
from database.drones_table import create_drone
from database.drone_updates_table import create_drone_update
from database.drone_events_table import create_drone_event_entry
from .users import get_current_user, is_admin
from ..dependencies import drones
from ..dependencies.drones import get_current_drone, generate_drone_token
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
async def drone_update(drone_id:int,
                        timestamp:datetime,
                        lon:float,
                        lat:float,
                        flight_range:int|None,
                        flight_time:int|None,
                        current_drone: Drone = Depends(get_current_drone)):
    """Api call te recieve updates from drones

    Args:
        update (DroneUpdate): updtade object
        current_drone (Drone, optional): drone to use. Defaults to Depends(get_current_drone).

    Returns:
        dict: response
    """
    if current_drone is None or current_drone.id != drone_id:
        return {"message": "invalid drone"}

    success = create_drone_update(
        current_drone.id,
        timestamp,
        lon,
        lat,
        flight_range,
        flight_time
    )
    if success:
        return {"message": "success"}
    else:
        return {"message": "error"}


@router.post("/drones/send-event/")
async def drone_event(
    drone_id: int,
    timestamp: datetime,
    lon: float,
    lat: float,
    event_type: int,
    confidence: int,
    csv_file_path: str | None = None,
    file_raw: UploadFile = File(),
    file_predicted: UploadFile = File(),
    current_drone: Drone = Depends(get_current_drone)):
    """Api call to recieve events form drones

    Args:
        event (DroneEvent): Event from the drone
        file (UploadFile): Associated image file
        current_drone (Drone, optional): Drone to use. Defaults to Depends(get_current_drone).

    Returns:
        dict: response
    """

    if current_drone is None:
        return {"message:": "Invalid drone" }
    try:
        event_location = os.getenv("EVENT_PATH")

        raw_file_location = f"{event_location}/{file_raw.filename}-{str(datetime.now())}"
        with open(raw_file_location, "wb+") as file_object:
            file_object.write(file_raw.file.read())

        predicted_file_location = f"{event_location}/{file_predicted.filename}-{str(datetime.now())}"
        with open(predicted_file_location, "wb+") as file_object:
            file_object.write(file_predicted.file.read())

        create_drone_event_entry(drone_id,
                                timestamp,
                                lon,
                                lat,
                                event_type,
                                confidence,
                                predicted_file_location,
                                csv_file_path)

        return {"raw_image_location": raw_file_location, "predicted_image_location": predicted_file_location}
    except Exception as err:
        print(err)
        return {"message": "error"}

@router.post("/drones/feedback/", status_code=status.HTTP_200_OK)
async def drone_feedback(reason: str,
                    notes: str,
                    file: UploadFile | None = File(),
                    current_user: User = Depends(get_current_user)):
    """API call to alarm the team

    Args:
        reason (str): drone
        notes (str): notes
        file (UploadFile | None, optional): file Defaults to File().
        current_user (User, optional): user. Defaults to Depends(get_current_user).

    Returns:
        dict: response
    """

    if not current_user:
        return {"message": "Invalid user"}

    feedback_location = os.getenv("DRONE_FEEDBACK_PATH")

    try:
        content = f"""
        reason: {reason}
        notes: {notes}
        """

        base_dir_path = f"{feedback_location}/{str(datetime.now())}"
        dir_path = base_dir_path
        i = 1
        while os.path.exists(dir_path):
            dir_path = base_dir_path + " - " + str(i)
            i = i + 1

        os.makedirs(dir_path)

        with open(f"{dir_path}/info.txt", "wb+") as file_object:
            file_object.write(content)

        file_location = f"{dir_path}/{file.filename}"
        with open(file_location, "wb+") as file_object:
            file_object.write(file.file.read())

        return {"message": "Feedback was send"}
    except Exception as err:
        print(err)
        return {"message": "Error while sending feedback"}

@router.post("/drones/signup/", status_code=status.HTTP_200_OK)
async def drone_signup(name: str,
                    drone_type: str,
                    flight_range: float,
                    cc_range: float,
                    flight_time: float,
                    current_user: User = Depends(get_current_user)):
    """creates a new drone

    Args:
        name (str): drone name
        drone_type (str): drone type
        flight_range (float): flight range
        cc_range (float): cc range
        flight_time (float): flight time
        current_user (User, optional): user. Defaults to Depends(get_current_user).

    Returns:
        dict: {drone, token}
    """

    if is_admin(current_user):
        drone = create_drone(name,drone_type,flight_range,cc_range,flight_time)
        return {"drone": drone, "token": generate_drone_token(drone)}
