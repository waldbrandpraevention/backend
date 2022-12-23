from .classes import Drone
from datetime import datetime, timedelta
import random

async def get_all_drones():
    """Returns all drones from the db

    Returns:
        Zone[]: List of drones
    """
    drones = []
    #TODO real db calls

    drones.append(Drone(name="drone-1",
                        last_update=datetime.now() - timedelta(days=random.randint(0,5), hours=random.randint(0,24)),
                        zone = "zone-123"))
    #drones.append(Drone("drone-2", datetime.now() - timedelta(days=random.randint(0,1), hours=random.randint(0,24)), "zone-123"))

    return drones

async def get_drone(name: str):
    """Returns a specific drone from the db

    Returns:
        Zone[]: List of zones
    """
    #TODO real db calls with None if not found

    return Zone(name, datetime.datetime.now())

async def get_drone_count():
    """Returns the amount of drones

    Returns:
        int: amount of drones
    """

    return len(await get_all_drones())