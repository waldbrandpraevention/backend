"""functions for api zones."""
from database import orga_zones_table

async def get_all_zones(orga_id:int):
    """Returns all zones from the db

    Args:
        orga_id (int): _description_

    Returns:
        Zone[]: List of zones
    """
    return orga_zones_table.get_zones_by_orga(orga_id)


async def get_zone_by_name(name: str, orga_id:int):
    """Returns a specific zone from the db

    Args:
        name (_type_): name of the zone.
        orga_id (_type_): id of the orga that want to access this zones data.

    Returns:
        Zone | None: zone object.
    """

    return orga_zones_table.get_orgazones_by_name(name,orga_id)

async def get_zone_by_id(zone_id: int, orga_id:int):
    """Returns a specific zone from the db

    Args:
        zone_id (_type_): id of the zone.
        orga_id (_type_): id of the orga that want to access this zones data.

    Returns:
        Zone | None: zone object.
    """
    return orga_zones_table.get_orgazones_by_id(zone_id,orga_id)

async def get_zone_count(orga_id:int):
    """Returns the amount of zones of this organization.

    Returns:
        int: amount of zones
    """
    fetched_zones = await get_all_zones(orga_id)
    if fetched_zones:
        count = len(fetched_zones)
    else:
        count = 0
    return count
