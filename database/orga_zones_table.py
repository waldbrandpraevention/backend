from enum import Enum
from typing import List

from api.dependencies.classes import Organization, Zone
from database.database import fetched_match_class
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
GET_ORGAZONES = '''  SELECT id,name,ST_AsText(area)
                    FROM zones
                    JOIN organization_zones 
                    ON zones.id = organization_zones.zone_id
                    WHERE organization_zones.orga_id=?;'''

GET_ZONEORGAS = ''' SELECT * 
                    FROM organizations
                    LEFT JOIN organization_zones 
                    ON organizations.id = organization_zones.orga_id
                    WHERE organization_zones.zone_id=?;'''

GET_ZONEBYNAME ='''SELECT id,name,ST_AsText(area) 
                    FROM zones
                    JOIN organization_zones 
                    ON zones.id = organization_zones.zone_id
                    WHERE zones.name=? 
                    AND organization_zones.orga_id=?;'''

GET_ORGAZONES_BY_ORGA = 'SELECT * FROM organization_zones WHERE orga_id=?;'
GET_ORGAZONES_BY_ZONE = 'SELECT * FROM organization_zones WHERE zone_id=?;'
UPDATE_ATTRIBUTE = 'UPDATE organization_zones SET {} = ? WHERE name = ?;'


def link_orgazone(orga_id:int,zone_id:int)->bool:
    inserted_id = db.insert(INSERT_ORGAZONE,(orga_id,zone_id))
    if inserted_id:
        return True
    
    return False

def get_zones_by_orga(orga_id:int) -> List[Zone] | None:
    fetched_zones = db.fetch_all(GET_ORGAZONES,(orga_id,))
    output = []
    for fetched in fetched_zones:
        zone = zones_table.get_obj_from_fetched(fetched)
        output.append(zone)
    return output

def get_orgas_by_zone(zone_id:int) -> Zone | None:
    fetched_orga = db.fetch_all(GET_ORGAZONES,(zone_id,))
    output = []
    for fetched in fetched_orga:
        orga = orgas_table.get_obj_from_fetched(fetched)
        output.append(orga)
    return output


def get_orgazones_by_name(name,orga_id) -> Zone | None:
    fetched_zone = db.fetch_one(GET_ZONEBYNAME,(name,orga_id))
    return zones_table.get_obj_from_fetched(fetched_zone)


def get_obj_from_fetched(fetched_orga):
    """generate Organization obj from fetched element.

    Args:
        fetched_orga (list): fetched attributes from orga.

    Returns:
        Organization: orga object.
    """
    if fetched_match_class(Organization,fetched_orga):
        orga_obj = Organization(
            id = fetched_orga[0],
            name=fetched_orga[1],
            abbreviation=fetched_orga[2]
        )
        return orga_obj
    return None