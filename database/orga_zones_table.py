from typing import List

from api.dependencies.classes import Organization, Zone
import database.database as db
from database import zones_table
import database.organizations_table as orgas_table

CREATE_ORGAZONES_TABLE = """ CREATE TABLE organization_zones
(
orga_id     integer NOT NULL ,
zone_id     integer NOT NULL ,
PRIMARY KEY (orga_id, zone_id),
FOREIGN KEY (orga_id) REFERENCES organizations (id),
FOREIGN KEY (zone_id) REFERENCES Zones (id)
);

CREATE INDEX IF NOT EXISTS organization_zones_FK_2 ON organization_zones (orga_id);
CREATE INDEX IF NOT EXISTS organization_zones_FK_3 ON organization_zones (zone_id);"""

INSERT_ORGAZONE =  "INSERT INTO organization_zones (orga_id,zone_id) VALUES (?,?);"


GET_ZONEORGAS = ''' SELECT *
                    FROM organizations
                    LEFT JOIN organization_zones 
                    ON organizations.id = organization_zones.orga_id
                    WHERE organization_zones.zone_id=?;'''

GET_ORGAZONES_BY_ORGA = 'SELECT * FROM organization_zones WHERE orga_id=?;'
GET_ORGAZONES_BY_ZONE = 'SELECT * FROM organization_zones WHERE zone_id=?;'
UPDATE_ATTRIBUTE = 'UPDATE organization_zones SET {} = ? WHERE name = ?;'


def link_orgazone(orga_id:int,zone_id:int)->bool:
    """link an organization with a zone.

    Args:
        orga_id (int): id of the orga that should be linked.
        zone_id (int): id of the zone that should be linked.

    Returns:
        bool: returns if action was successful.
    """
    inserted_id = db.insert(INSERT_ORGAZONE,(orga_id,zone_id))
    if inserted_id:
        return True
    
    return False

def get_zones_by_orga(orga_id:int) -> List[Zone] | None:
    """fetches all zones, linked to an organization.

    Args:
        orga_id (int): id of the orga.

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
        name (_type_): name of the zone.
        orga_id (_type_): id of the orga that want to access this zones data.

    Returns:
        Zone | None: zone object.
    """
    sql = zones_table.GET_ZONEJOINORGA.format('name')
    fetched_zone = db.fetch_one(sql,(name,orga_id))
    return zones_table.get_obj_from_fetched(fetched_zone)

def get_orgazones_by_id(zone_id,orga_id) -> Zone | None:
    """fetch the zone by its id and make sure its a zone that the orga is allowed to see.

    Args:
        zone_id (_type_): id of the zone.
        orga_id (_type_): id of the orga that want to access this zones data.

    Returns:
        Zone | None: zone object.
    """
    sql = zones_table.GET_ZONEJOINORGA.format('id')
    fetched_zone = db.fetch_one(sql,(zone_id,orga_id))
    return zones_table.get_obj_from_fetched(fetched_zone)