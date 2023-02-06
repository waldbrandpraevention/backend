"""Drone related functions"""
import datetime
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
            set_update_and_zone(drone,drone_upate)

    return drones

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
        set_update_and_zone(drone,drone_upate)

    return drone

async def get_drone_events(orga_id:int,
                           timestamp:datetime.datetime,
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

async def set_update_and_zone(drone:Drone,drone_upate:DroneUpdate):
    """Sets the last update and the zone of a drone

    Args:
        drone (Drone): the drone
        drone_upate (DroneUpdate): the last update of the drone
    """
    drone.last_update = drone_upate.timestamp
    current_zone = zones_table.get_zone_of_coordinate(
                                drone_upate.lon,
                                drone_upate.lat
                                )
    if current_zone is not None:
        drone.zone_id = current_zone.id

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
