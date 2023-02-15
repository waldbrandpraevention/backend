"""Drone related functions"""
import datetime, timedelta
from .authentication import create_access_token, DRONE_TOKEN_EXPIRE_WEEKS
from typing import List
from fastapi import HTTPException, status
from api.dependencies.classes import Drone, DroneEvent, DroneUpdate, DroneUpdateWithRoute
from database import (drones_table,
                      drone_events_table,
                      drone_updates_table as drone_data_table,
                      zones_table)
from database.orga_zones_table import get_orgazones_by_id

async def get_all_drones(orga_id:int):
    """Returns all drones from the db

    Returns:
        Zone[]: List of drones
    """
    drones = []

    drones = drones_table.get_drones(orga_id)

    for drone in drones:
        drone_upate = drone_data_table.get_latest_update(drone.id)
        if drone_upate is not None:
           await set_update_and_zone(drone,drone_upate)

    return drones

async def generate_drone_token(id: int):
    """Returns a new drone token

    Returns:
        Token: new token
    """
    access_token_expires = timedelta(minutes=DRONE_TOKEN_EXPIRE_WEEKS)
    access_token = create_access_token(
        data={"sub": id}, expires_delta=access_token_expires
    )

    return access_token

async def get_drone(drone_id: int,orga_id:int):
    """Returns a specific drone from the db

    Returns:
        Drone: the requestesd drone
    """
    drone = drones_table.get_drone(drone_id,orga_id)
    if drone is None:
        return None
    drone_upate = drone_data_table.get_latest_update(drone_id)
    if drone_upate:
        await set_update_and_zone(drone,drone_upate)

    return drone

async def get_drone_for_token(drone_id: int, orga_id: int):
    """Returns a specific drone from the db

    Returns:
        Drone: the requestesd drone
    """
    drone = drones_table.get_drone(drone_id,orga_id)
    drone_upate = drone_data_table.get_latest_update(drone.id)
    if drone_upate:
        set_update_and_zone(drone,drone_upate)

    return drone

async def get_current_drone(token: str):
    """Returns the current drone

    Args:
        token (str): token

    Returns:
        Drone: Drone object of the current drone
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token data is invalid",
        headers={"WWW-Authenticate": "Bearer"},
    )
    drone_id = await get_email_from_token(token) #returns id as well
    drone = get_drone_for_token(drone_id)
    if drone is None:
        raise credentials_exception

    return drone
   
async def get_drone_events(orga_id:int,
                           timestamp: datetime,
                           drone_id:int =None,
                           zone_id:int=None) -> List[DroneEvent]:
    """get all drone events in a zone or the whole orga area after a timestamp.

    Args:
        orga_id (int): id of the orga.
        timestamp (datetime.datetime): timestamp after which the events should be returned.
        drone_id (int, optional): id of the drone. Defaults to None.
        zone_id (int, optional): id of the zone. Defaults to None.

    Raises:
        HTTPException: if the zone id is invalid.

    Returns:
        List[DroneEvent]: list of drone events filtered by the given parameters.
    """
    if zone_id is not None:
        polygon = zones_table.get_zone_polygon(zone_id)
        if polygon is None:
            raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Invalid Zone ID",
        )
    else:
        polygon = zones_table.get_orga_area(orga_id)[0]

    return drone_events_table.get_drone_event(polygon=polygon,drone_id=drone_id,after=timestamp)



async def set_update_and_zone(drone:Drone,drone_upate:DroneUpdate):
    """gets the id of the zone, the drone is in.

    Args:
        drone (Drone): _description_
        drone_upate (DroneUpdate): _description_
    """
    drone.last_update = drone_upate.timestamp
    current_zone = zones_table.get_zone_of_coordinate(
                                drone_upate.longitude,
                                drone_upate.latitude)
    if current_zone is not None:
        drone.zone_id = current_zone.id

async def get_drone_with_route( orga_id:int,
                                timestamp:datetime.datetime,
                                drone_id:int =None,
                                zone_id:int=None
                                )-> List[DroneUpdateWithRoute] | None:
    """get all drone updates in a zone or the whole orga area after a timestamp.

    Args:
        orga_id (int): id of the orga.
        timestamp (datetime.datetime): timestamp after which the events should be returned.
        drone_id (int, optional): id of the drone. Defaults to None.
        zone_id (int, optional): id of the zone. Defaults to None.

    Raises:
        HTTPException: if the zone id is invalid.

    Returns:
        DroneUpdateWithRoute | None: list of drone updates filtered by the given parameters.
    """

    if zone_id is not None:
        polygon = zones_table.get_zone_polygon(zone_id)
        if polygon is None:
            raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Invalid Zone ID",
        )
    else:
        polygon = zones_table.get_orga_area(orga_id)[0]

    return drone_data_table.get_drone_updates(polygon=polygon,
                                              drone_id=drone_id,
                                              after=timestamp,
                                              get_coords_only=True)

async def get_drone_count(zone_id:int,orga_id:int):
    """Returns the amount of drones

    Returns:
        int: amount of drones
    """

    zone = get_orgazones_by_id(zone_id,orga_id)
    if zone is not None:
        return zone.drone_count

    raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Zone ID invalid or not linked to your Orga.",
        )
