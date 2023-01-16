from .classes import Zone
from database import zones_table


async def get_zone(name: str):
    """Returns a zone from the db

    Returns:
        Zone: zone
    """
    zone = None #TODO add db call

    return zone

async def get_all_zones():
    """Returns all zones from the db

    Returns:
        Zone[]: List of zones
    """
    zones = get_zones()

    return zones

async def get_zone_count():
    """Returns the amount of drones

    Returns:
        int: amount of drones
    """
    return len(await get_all_zones())