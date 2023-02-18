"""File containing all the dependencies for the territories."""

from api.dependencies.classes import Territory
from database import territories_table


async def get_territories(orga_id):
    """get all territories linked to an organization.

    Args:
        orga_id (int): id of the organization.

    Returns:
        list: list of all territories.
    """

    return territories_table.get_territories(orga_id)

async def get_territory_by_id(territory_id:int, orga_id:int) -> Territory | None:
    """get a territory by id. The territory has to be linked to the orga.

    Args:
        territory_id (int): the id of the territory to fetch.
        orga_id (int): id of the organization that the territory belongs to.

    Returns:
        Territory: the territory object.
    """
    territory = territories_table.get_territory(territory_id)
    if territory is None or territory.orga_id != orga_id:
        return None
    return territory
