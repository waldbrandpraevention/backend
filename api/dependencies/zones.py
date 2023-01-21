
from database import orga_zones_table

async def get_all_zones(orga_id:int):
    """Returns all zones from the db

    Args:
        orga_id (int): _description_

    Returns:
        Zone[]: List of zones
    """
    return orga_zones_table.get_zones_by_orga(orga_id)


async def get_zone(name: str, orga_id:int):
    """Returns a specific zone from the db

    Returns:
        Zone[]: List of zones
    """

    return orga_zones_table.get_orgazones_by_name(name,orga_id)

async def get_zone_count(orga_id:int):
    """Returns the amount of drones

    Returns:
        int: amount of drones
    """
    return len(await get_all_zones(orga_id))