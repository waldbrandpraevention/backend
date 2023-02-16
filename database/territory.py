"""This module contains the territory table and its related functions."""
from typing import List
from database import drone_events_table, zones_table
import database.database as db
from api.dependencies.classes import Territory, TerritoryWithZones, Zone

CREATE_TERRITORY_TABLE = '''CREATE TABLE IF NOT EXISTS territories
(
id           integer NOT NULL ,
orga_id      integer NOT NULL ,
name         text NOT NULL ,
desscription text NOT NULL ,
PRIMARY KEY (id)
);
CREATE UNIQUE INDEX IF NOT EXISTS territory_AK ON territories (name,orga_id);'''
# unique index on name and orga_id, so that no two territories
# with the same name can be created in the same organization.

INSERT_TERRITORY = 'INSERT INTO territories (orga_id, name, desscription) VALUES (?,?,?);'
UPDATE_TERRITORY = 'UPDATE territories SET {} = ? WHERE name = ?;'
GET_TERRITORY = '''SELECT id,orga_id,name,desscription
                    FROM territories
                    {};'''
GET_TERRITORY_IDS = '''SELECT id
                    FROM territories
                    {};'''

def create_territory(orga_id: int, name: str, description: str) -> int | None:
    """create a territory.

    Args:
        orga_id (int): id of the organization that the territory belongs to.
        name (str): name of the territory.
        description (str): description of the territory.

    Returns:
        int | None: Id of the inserted entry, None if an error occurs.
    """
    return db.insert(INSERT_TERRITORY, (orga_id, name, description))

def get_territory(territory_id: int) -> Territory:
    """fetch a territory.

    Args:
        territory_id (int): id of the territory to fetch.

    Returns:
        Territory: the territory object.
    """
    fetched_territory = db.fetch_one(GET_TERRITORY.format('WHERE id = ?'), (territory_id,))
    return get_obj_from_fetched(fetched_territory)

def get_territories(orga_id: int) -> List[Territory]:
    """fetch all territories.

    Args:
        orga_id (int): id of the organization that the territories belong to.

    Returns:
        list: list of all territories.
    """
    fetched_territories = db.fetch_all(GET_TERRITORY.format('WHERE orga_id = ?'), (orga_id,))
    if fetched_territories is None:
        return None
    output = []
    for territory in fetched_territories:
        territory_obj = get_obj_from_fetched(territory)
        if territory_obj:
            output.append(territory_obj)
    return output

def get_territory_zones(orga_id: int) -> List[Zone]:
    """fetch all zones.

    Args:
        orga_id (int): id of the organization that the zones belong to.

    Returns:
        list: list of all zones.
    """
    terri_ids = db.fetch_all(GET_TERRITORY.format('WHERE orga_id = ?'), (orga_id,))
    if terri_ids is None:
        return None
    output = []
    for zone in fetched_zones:
        zone_obj = zones_table.get_obj_from_fetched(zone)
        if zone_obj:
            output.append(zone_obj)
    return output

    

def get_obj_from_fetched(fetched_territory: tuple) -> TerritoryWithZones:
    """get a territory object from a fetched tuple.

    Args:
        fetched_territory (tuple): the fetched tuple.

    Returns:
        Territory: the territory object.
    """
    if not db.fetched_match_class(Territory, fetched_territory):
        return None
    territory_id, orga_id, name, description = fetched_territory

    areas = drone_events_table.get_areas_in_territory(territory_id)

    events = drone_events_table.get_drone_event(
                                    polygon=fetched_zone[4], 
                                    after=after)

    last_update = drone_updates_table.get_lastest_update_in_zone(
                    fetched_zone[4])
    if last_update is not None:
        la_timestam = last_update.timestamp
    else:
        la_timestam = None

    if events:
        ai_firerisk_enum = drone_events_table.calculate_firerisk(events)
    else:
        ai_firerisk_enum = FireRisk(1)

    #dwd_fire_risk: FireRisk | None = None
    # ai_fire_risk: FireRisk | None = None
    # drone_count: int | None = None
    # zone_count: int | None = None
    # last_update: datetime | None = None
    return TerritoryWithZones(territory_id,
                              orga_id,
                              name,
                              description,
                              ai_firerisk_enum,
                              dwd_fire_risk,
                              drone_count,
                              zone_count,
                              la_timestam)

