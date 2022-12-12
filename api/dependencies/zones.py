from .classes import Zone

def get_all_zones():
    """Returns all zones from the db

    Returns:
        Zone[]: List of zones
    """
    zones = []
    #TODO real db calls

    zones.append(Zone("Zone-123", 1))
    zones.append(Zone("Zone-345", 1))

    return zones

def get_zone(name: str):
    """Returns a specific zone from the db

    Returns:
        Zone[]: List of zones
    """
    #TODO real db calls with None if not found

    return Zone(name, 1)