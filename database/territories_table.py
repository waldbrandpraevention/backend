""" This module contains the territory table and its related functions.
    A Territory is a collection of zones.
    It is used to group zones together and to assign them to a specific organization.

"""
from typing import List
from database import drone_events_table, zones_table
import database.database as db
from database.spatia import spatiageostr_to_geojson
from api.dependencies.classes import FireRisk, TerritoryWithZones, Zone


CREATE_TERRITORY_TABLE = '''CREATE TABLE IF NOT EXISTS territories
(
id           integer NOT NULL ,
orga_id      integer NOT NULL ,
name         text NOT NULL ,
description text,
PRIMARY KEY (id),
FOREIGN KEY (orga_id) REFERENCES organizations (id)
);
CREATE UNIQUE INDEX IF NOT EXISTS territory_AK ON territories (name,orga_id);'''
# unique index on name and orga_id, so that no two territories
# with the same name can be created in the same organization.

INSERT_TERRITORY = 'INSERT INTO territories (orga_id, name, description) VALUES (?,?,?);'
UPDATE_TERRITORY = 'UPDATE territories SET {} = ? WHERE name = ?;'

GET_TERRITORY = '''SELECT id,orga_id,name,description
                    FROM territories
                    Jo
                    {};'''

GET_TERRITORY_IDS = '''SELECT id
                    FROM territories
                    {};'''

GET_ORGA_TERRITORIES = """
SELECT 
territories.id,
territories.orga_id,
territories.name,
territories.description,
AsGeoJSON(GUnion(area)) as oarea,
X(ST_Centroid(GUnion(area)))as lon,
Y(ST_Centroid(GUnion(area)))as lat,
newdrone_data.ts,
COUNT(DISTINCT drone_id),
COUNT(DISTINCT territory_zones.zone_id)
from zones
JOIN territory_zones ON zones.id = territory_zones.zone_id
JOIN territories ON territories.id = territory_zones.territory_id
LEFT OUTER JOIN (
        SELECT coordinates, MAX(timestamp) as ts, drone_id
        from drone_data
        group by drone_data.drone_id
    ) AS newdrone_data
ON ST_Intersects(newdrone_data.coordinates, area)
{}
;"""

GET_ORGA_AREA = """
SELECT 
AsGeoJSON(GUnion(area)) as oarea
from zones
JOIN territory_zones 
ON zones.id = territory_zones.zone_id
JOIN territories ON territories.id = territory_zones.territory_id
WHERE territories.orga_id = ?
;"""

def create_territory(orga_id: int, name: str, description: str=None) -> int | None:
    """create a territory.

    Args:
        orga_id (int): id of the organization that the territory belongs to.
        name (str): name of the territory.
        description (str): description of the territory. Defaults to None.

    Returns:
        int | None: Id of the inserted entry, None if an error occurs.
    """
    return db.insert(INSERT_TERRITORY, (orga_id, name, description))

def get_territory(territory_id: int) -> TerritoryWithZones:
    """get a territory by its id.

    Args:
        territory_id (int): id of the territory to fetch.

    Returns:
        Territory: the territory object.
    """
    sql = GET_ORGA_TERRITORIES.format('WHERE territories.id = ?')
    fetched_territory = db.fetch_one(sql, (territory_id,))
    if fetched_territory is None or fetched_territory[0] is None:
        return None

    return get_obj_from_fetched(fetched_territory)

def get_territories(orga_id: int) -> List[TerritoryWithZones]:
    """fetch all territories.

    Args:
        orga_id (int): id of the organization that the territories belong to.

    Returns:
        list: list of all territories, linked to the organization.
    """
    sql = GET_ORGA_TERRITORIES.format('WHERE territories.orga_id = ?')
    fetched_territories = db.fetch_all(sql, (orga_id,))
    if fetched_territories is None:
        return None
    output = []
    for territory in fetched_territories:
        territory_obj = get_obj_from_fetched(territory)
        if territory_obj:
            output.append(territory_obj)
    return output

def get_orga_area(orga_id) -> str | None:
    """fetch the area of all territories of an organization.

    Args:
        orga_id (int): id of the organization that the territories belong to.

    Returns:
        str | None: the area of all territories of an organization. As a geojson string.
    """

    polygon = db.fetch_one(GET_ORGA_AREA, (orga_id,))
    if polygon is not None:
        return polygon[0]
    return None

def get_territory_zones(orga_id: int) -> List[Zone]:
    """fetch all zones of all territories of an organization.

    Args:
        orga_id (int): id of the organization that the zones belong to.

    Returns:
        list: list of all zones.
    """
    oraga_area = get_orga_area(orga_id)
    return zones_table.get_zones_in_area(oraga_area)


def get_obj_from_fetched(fetched_territory: tuple) -> TerritoryWithZones:
    """get a territory object from a fetched tuple.

    Args:
        fetched_territory (tuple): the fetched tuple.

    Returns:
        Territory: the territory object.
    """
    if not db.fetched_match_class(TerritoryWithZones, fetched_territory, subtract=2):
        return None

    geo_json = spatiageostr_to_geojson(fetched_territory[4])

    events = drone_events_table.get_drone_event(
                                    polygon=fetched_territory[4])

    la_timestam = fetched_territory[7]


    if events:
        try:
            ai_firerisk_enum = drone_events_table.calculate_firerisk(events)[0]
        except IndexError:
            ai_firerisk_enum = FireRisk(0)
    else:
        ai_firerisk_enum = FireRisk(0)

    zone_count = fetched_territory[9]

    try:
        lon = fetched_territory[5]
        lat= fetched_territory[6]
    except IndexError:
        lon = None
        lat= None

    return TerritoryWithZones(id=fetched_territory[0],
                              orga_id=fetched_territory[1],
                              name=fetched_territory[2],
                              description=fetched_territory[3],
                              dwd_fire_risk=None,
                              ai_fire_risk=ai_firerisk_enum,
                              drone_count=fetched_territory[8],
                              zone_count=zone_count,
                              last_update=la_timestam,
                              geo_json=geo_json,
                              lon=lon,
                              lat=lat)
