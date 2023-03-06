"""DB functions for orga teritories.
    Here you can link zones to territories, which are linked to organizations. 
"""
from typing import List

from api.dependencies.classes import Organization, Zone
import database.database as db
from database import zones_table
import database.organizations_table as orgas_table

CREATE_TERRITORYZONES_TABLE = """ CREATE TABLE territory_zones
(
territory_id     integer NOT NULL ,
zone_id     integer NOT NULL ,
PRIMARY KEY (territory_id, zone_id),
FOREIGN KEY (territory_id) REFERENCES territories (id),
FOREIGN KEY (zone_id) REFERENCES Zones (id)
);

CREATE INDEX IF NOT EXISTS territory_zones_FK_2 ON territory_zones (territory_id);
CREATE INDEX IF NOT EXISTS territory_zones_FK_3 ON territory_zones (zone_id);"""

INSERT_ORGAZONE =  "INSERT INTO territory_zones (territory_id,zone_id) VALUES (?,?);"


GET_ZONEORGAS = ''' SELECT *
                    FROM organizations
                    Join territories on organizations.id = territories.orga_id
                    JOIN territory_zones 
                    ON territories.id = territory_zones.territory_id
                    WHERE territory_zones.zone_id=?;'''

GET_ORGAZONES_BY_ORGA = 'SELECT zone_id FROM territory_zones WHERE territory_id=?;'
GET_ORGAZONES_BY_ZONE = 'SELECT territory_id FROM territory_zones WHERE zone_id=?;'
UPDATE_ATTRIBUTE = 'UPDATE territory_zones SET {} = ? WHERE name = ?;'


def link_territory_zone(territory_id:int,zone_id:int)->bool:
    """link a territory with a zone.

    Args:
        territory_id (int): id of the territory that should be linked.
        zone_id (int): id of the zone that should be linked.

    Returns:
        bool: returns if action was successful.
    """
    inserted_id = db.insert(INSERT_ORGAZONE,(territory_id,zone_id))
    if inserted_id:
        return True

    return False

def get_zones_by_orga(orga_id:int) -> List[Zone] | None:
    """fetches all zones, linked to an organization.

    Args:
        territory_id (int): id of the territory.

    Returns:
        List[Zone] | None: list of zones.
    """
    fetched_zones = db.fetch_all(zones_table.GET_ORGAZONES,(orga_id,))
    if fetched_zones is None:
        return None
    output = []
    for fetched in fetched_zones:
        zone = zones_table.get_obj_from_fetched(fetched)
        output.append(zone)
    return output

def get_orgas_by_zone(zone_id:int) -> List[Organization] | None:
    """get orgas that are linked to this zone.

    Args:
        zone_id (int): id of the zone.

    Returns:
        List[Organization] | None: list of orgas.
    """
    fetched_orga = db.fetch_all(GET_ZONEORGAS,(zone_id,))
    if fetched_orga is None:
        return None
    output = []
    for fetched in fetched_orga:
        orga = orgas_table.get_obj_from_fetched(fetched)
        output.append(orga)
    return output

def get_orgazones_by_name(name,orga_id) -> Zone | None:
    """fetch the zone by its name and make sure its a zone that the orga is allowed to see.

    Args:
        name (str): name of the zone.
        orga_id (int): id of the orga that want to access this zones data.

    Returns:
        Zone | None: zone object.
    """
    sql = zones_table.GET_ZONEJOINORGA.format('name')
    fetched_zone = db.fetch_one(sql,(name,orga_id))
    return zones_table.get_obj_from_fetched(fetched_zone)

def get_orgazone_by_id(zone_id,orga_id) -> Zone | None:
    """fetch the zone by its id and make sure its a zone that the orga is allowed to see.

    Args:
        zone_id (int): id of the zone.
        orga_id (int): id of the orga that want to access this zones data.

    Returns:
        Zone | None: zone object.
    """
    sql = zones_table.GET_ZONEJOINORGA.format('id')
    fetched_zone = db.fetch_one(sql,(zone_id,orga_id))
    return zones_table.get_obj_from_fetched(fetched_zone)
