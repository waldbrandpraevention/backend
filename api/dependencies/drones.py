"""functions for drone api."""
import datetime
from api.dependencies.classes import Drone, DroneUpdate
from database import (drones_table,
                      drone_events_table,
                      drone_updates_table as drone_data_table,
                      zones_table)
from fastapi import HTTPException, status

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
    drone_upate = drone_data_table.get_latest_update(drone.id)
    if drone_upate:
        set_update_and_zone(drone,drone_upate)

    return drone

async def get_drone_events(orga_id:int,
                           timestamp:datetime.datetime,
                           drone_id:int =None,
                           zone_id:int=None):
    
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
                                drone_upate.latitude
                                )
    if current_zone is not None:
        drone.zone_id = current_zone.id

async def get_drone_count():
    """Returns the amount of drones

    Returns:
        int: amount of drones
    """

    return len(await get_all_drones())