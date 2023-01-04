from .classes import Drone
from datetime import datetime, timedelta
import random
from database import drones as drones_table
from database import drone_data as drone_data_table

async def get_all_drones():
    """Returns all drones from the db

    Returns:
        Zone[]: List of drones
    """
    drones = []
    
    drones = drones_table.get_drones()

    for drone in drones:
        drone_data = drone_data_table.get_latest_by_timestamp(drone.id)
        if drone_data:
            drone.last_update = drone_data.timestamp
            #TODO Get Zone by lat and long

    return drones

async def get_drone(name: str):
    """Returns a specific drone from the db

    Returns:
        Drone: the requestesd drone
    """
    drone = drones_table.get_drone(name)
    drone_data = drone_data_table.get_latest_by_timestamp(drone.id)
    if drone_data:
        drone.last_update = drone_data.timestamp
        #TODO Get Zone by lat and long

    return drone

async def get_drone_count():
    """Returns the amount of drones

    Returns:
        int: amount of drones
    """

    return len(await get_all_drones())