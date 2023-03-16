"""api calls for drones."""
import os
from datetime import datetime
from typing import List
from fastapi import Depends, APIRouter, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse
from database.drones_table import create_drone
from database.drone_updates_table import create_drone_update
from database.drone_events_table import create_drone_event_entry, get_event_by_id
from .users import get_current_user, is_admin
from ..dependencies import drones
from ..dependencies.drones import generate_drone_token, validate_token
from ..dependencies.classes import Drone, DroneEvent, DroneUpdateWithRoute, User
from ..dependencies.zones import get_zone_by_id

router = APIRouter()

@router.get("/drones/", status_code=status.HTTP_200_OK, response_model=Drone)
async def read_drone(drone_id: int, current_user: User = Depends(get_current_user)):
    """API call to get a specific drone

    Args:
        name (str): Name of the drone
        current_user (User, optional): User. Defaults to User that is logged in.

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
        zone_id (int, optional): id of the zone the drone is in. Defaults to None.
        days (int, optional): days before now. Defaults to 0.
        hours (int, optional): hours before now. Defaults to 0.
        minutes (int, optional): minutes before now. Defaults to 0.
        current_user (User, optional): User. Defaults to User that is logged in.

    Returns:
        List[DroneEvent]: List of drone events.
    """

    timestamp = drones.timestamp_helper(days,hours,minutes)
    fetched_drone_events = await drones.get_drone_events(orga_id=current_user.organization.id,
                                           timestamp=timestamp,
                                           drone_id=drone_id,
                                           zone_id=zone_id)

    if fetched_drone_events is None:
        return []

    return fetched_drone_events

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
    """API call to get the route of a drone in a specific time frame and/or zone.
    Returns the last update and the route, the drone took to get to the last update.

    Args:
        drone_id (int, optional): id of the drone. Defaults to None.
        zone_id (int, optional): id of the zone the drone is in. Defaults to None.
        days (int, optional): days before now. Defaults to 0.
        hours (int, optional): hours before now. Defaults to 0.
        minutes (int, optional): minutes before now. Defaults to 0.
        current_user (User, optional): User. Defaults to User that is logged in.

    Returns:
        List[DroneUpdateWithRoute]: List of drones updates with their route.
    """

    timestamp = drones.timestamp_helper(days,hours,minutes)
    drone_updates = await drones.get_drone_with_route(orga_id=current_user.organization.id,
                                            zone_id=zone_id,
                                           timestamp=timestamp,
                                           drone_id=drone_id)
    if drone_updates is None:
        return []

    return drone_updates

@router.get("/drones/all/",
            status_code=status.HTTP_200_OK,
            response_model=List[Drone])
async def read_drones_all(current_user: User = Depends(get_current_user)):
    """API call to get the all drones

    Args:
        current_user (User, optional): User. Defaults to User that is logged in.

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
    """API call to get the count of drones in a zone

    Args:
        zone_id (int): id of the zone
        current_user (User, optional): User. Defaults to User that is logged in.

    Returns:
        int: count of drones
    """
    return await drones.get_drone_count(zone_id,current_user.organization.id)

@router.post("/drones/send-update/", status_code=status.HTTP_200_OK)
async def drone_update(drone_id:int,
                        timestamp:datetime,
                        lon:float,
                        lat:float,
                        flight_range:float|None,
                        flight_time:float|None,
                        current_drone_token: str):
    """Api call te recieve updates from drones

    Args:
        update (DroneUpdate): updtade object
        current_drone (Drone, optional): drone to use. Defaults to Depends(get_current_drone).

    Returns:
        dict: response
    """

    if not await validate_token(current_drone_token) :
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Invalid drone",
        )

    #timestamp = datetime.fromtimestamp(unixtimestamp)
    success = create_drone_update(
        drone_id,
        timestamp,
        lon,
        lat,
        flight_range,
        flight_time
    )
    if success:
        return {"message": "success"}

    return {"message": "error"}


@router.post("/drones/send-event/")
async def drone_event(
    drone_id: int,
    lon: float,
    lat: float,
    event_type: int,
    confidence: int,
    current_drone_token: str,
    file_raw: UploadFile,
    file_predicted:UploadFile,
    timestamp: datetime,
    csv_file_path: str | None = None,
    ):
    """Api call to recieve events form drones

    Args:
        event (DroneEvent): Event from the drone
        file (UploadFile): Associated image file
        current_drone (Drone, optional): Drone to use. Defaults to Depends(get_current_drone).

    Returns:
        dict: response
    """

    if not await validate_token(current_drone_token):
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Invalid drone",
        )

    event_location = os.getenv("EVENT_PATH")
    if not os.path.exists(event_location):
        os.makedirs(event_location)


    sub_folder = str(timestamp).replace(" ", "")
    sub_path = os.path.join(event_location, sub_folder)
    if not os.path.exists(sub_path):
        os.makedirs(sub_path)
    else:
        return {"location": sub_path}

    raw_file_location = f"{sub_path}/raw.jpg"
    with open(raw_file_location, "wb+") as file_object:
        file_object.write(file_raw.file.read())

    predicted_file_location = f"{sub_path}/predicted.jpg"
    with open(predicted_file_location, "wb+") as file_object:
        file_object.write(file_predicted.file.read())

    create_drone_event_entry(drone_id,
                            timestamp,
                            lon,
                            lat,
                            event_type,
                            confidence,
                            sub_path,
                            csv_file_path)

    return {"location": sub_path}

@router.post("/drones/send-events/")
async def drone_events(events: List[DroneEvent], files: UploadFile, token: str):
    """Api call to recieve multiple events from one drone

    Args:
        event (DroneEvent): Event from the drone
        file (UploadFile): Associated image file
        current_drone (Drone, optional): Drone to use. Defaults to Depends(get_current_drone).

    Returns:
        dict: response
    """
    try:
        file_raw = files[0]
        file_predicted = files[1]
    except IndexError as err:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Invalid number of files",
        ) from err

    for event in events:
        if not await validate_token(token):
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="Invalid drone",
            )

        event_location = os.getenv("EVENT_PATH")
        if not os.path.exists(event_location):
            os.makedirs(event_location)

        sub_folder = str(event.timestamp)
        sub_path = os.path.join(event_location, sub_folder)
        if not os.path.exists(sub_path):
            os.makedirs(sub_path)
        else:
            return {"location": sub_path}

        raw_file_location = f"{sub_path}/raw.jpg"
        with open(raw_file_location, "wb+") as file_object:
            file_object.write(file_raw.file.read())

        predicted_file_location = f"{sub_path}/predicted.jpg"
        with open(predicted_file_location, "wb+") as file_object:
            file_object.write(file_predicted.file.read())

        create_drone_event_entry(event.drone_id,
                                event.timestamp,
                                event.lon,
                                event.lat,
                                event.event_type,
                                event.confidence,
                                sub_path,
                                event.csv_file_path)

    return {"location": sub_path}


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
        current_user (User, optional): User. Defaults to User that is logged in.

    Returns:
        dict: response
    """

    if not current_user:
        return {"message": "Invalid user"}

    feedback_location = os.getenv("DRONE_FEEDBACK_PATH")
    if not os.path.exists(feedback_location):
        os.makedirs(feedback_location)

    try:
        content = f"""
        reason: {reason}
        notes: {notes}
        """

        sub_path = os.path.join(feedback_location, str(datetime.now()))

        if not os.path.exists(sub_path):
            os.makedirs(sub_path)

        with open(f"{sub_path}/info.txt", "wb+") as file_object:
            file_object.write(content)

        file_location = f"{sub_path}/{file.filename}"
        with open(file_location, "wb+") as file_object:
            file_object.write(file.file.read())

        return {"message": "Feedback was send"}
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Error while sending",
        ) from err

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
        current_user (User, optional): User. Defaults to User that is logged in.

    Returns:
        dict: {drone, token}
    """
    if await is_admin(current_user):
        drone = create_drone(name,drone_type,flight_range,cc_range,flight_time)
        return {"drone": drone, "token": await generate_drone_token(drone)}


@router.get("/drones/get-event-image-raw/", response_class=FileResponse)
async def get_image_raw(event_id: int,
                    current_user: User = Depends(get_current_user)):
    """Returns the raw image related to an event

    Args:
        event_id (int): event id of the event
        current_user (User, optional): _description_. Defaults to Depends(get_current_user).

    Returns:
        FileResponse: image
    """
    curr_drone_event = get_event_by_id(event_id)
    print(curr_drone_event)
    if curr_drone_event is None:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Event does not exist in the database",
        )
    if await get_zone_by_id(curr_drone_event.zone_id, current_user.organization.id) is None:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="User is not allowed to access this event. The zone of the event is most likly not part of your organization.",
        )
    path = os.path.join(curr_drone_event.picture_path, "raw.jpg")
    if os.path.exists(path):
        return path

    path = path.strip("/")
    if os.path.exists(path):
        return path

    raise HTTPException(
        status_code=status.HTTP_406_NOT_ACCEPTABLE,
        detail=f"Event exists but there are no images for it. Path = {path}",
    )


@router.get("/drones/get-event-image-predicted/", response_class=FileResponse)
async def get_image_predicted(event_id: int,
                    current_user: User = Depends(get_current_user)):
    """Returns the predicted image related to an event

    Args:
        event_id (int): event id of the event
        current_user (User, optional): _description_. Defaults to Depends(get_current_user).

    Returns:
        FileResponse: image
    """

    curr_drone_event = get_event_by_id(event_id)
    print(curr_drone_event)
    if curr_drone_event is None:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Event does not exist in the database",
        )
    if await get_zone_by_id(curr_drone_event.zone_id, current_user.organization.id) is None:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="User is not allowed to access this event. The zone of the event is most likly not part of your organization.",
        )
    path = os.path.join(curr_drone_event.picture_path, "predicted.jpg")
    if os.path.exists(path):
        return path

    path = path.strip("/")
    if os.path.exists(path):
        return path

    raise HTTPException(
        status_code=status.HTTP_406_NOT_ACCEPTABLE,
        detail=f"Event exists but there are no images for it. Path = {path}",
    )
