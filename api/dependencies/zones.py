from .classes import Zone

async def get_all_zones():
    """Returns all zones from the db

    Returns:
        Zone[]: List of zones
    """
    zones = []
    #TODO real db calls

    zones.append(Zone(name="Zone-123", fire_risk=1, ai=1))
    zones.append(Zone(name="Zone-456", fire_risk=1, ai=1))

    return zones

async def get_zone(name: str):
    """Returns a specific zone from the db

    Returns:
        Zone[]: List of zones
    """
    #TODO real db calls with None if not found

    return Zone(name, 1)

async def get_zone_count():
    """Returns the amount of drones

    Returns:
        int: amount of drones
    """
    return len(await get_all_zones())