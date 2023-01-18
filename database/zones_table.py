

from typing import List
from api.dependencies.classes import FireRisk, Zone
from database.database import fetched_match_class
from database.spatia import spatiapoly_to_long_lat_arr, coordinates_to_polygon
from database.drone_events_table import get_drone_events_in_zone
import database.database as db

CREATE_ZONE_TABLE = '''CREATE TABLE zones
(
id       integer NOT NULL ,
name    text NOT NULL ,
PRIMARY KEY (id)
);

SELECT AddGeometryColumn('zones', 'area', 4326, 'POLYGON', 'XY');'''
#   POLYGON((101.23 171.82, 201.32 101.5, 215.7 201.953, 101.23 171.82))
#   exterior ring, no interior rings
CREATE_ENTRY = 'INSERT INTO zones (name,area) VALUES (?,GeomFromText(?, 4326));'

GET_ZONE = '''SELECT id,name, ST_AsText(area) AS area FROM zones
                JOIN ElementaryGeometries AS e ON (e.f_table_name = 'zones' 
                AND e.origin_rowid = zones.rowid)
                WHERE ST_Intersects(area, MakePoint(?, ?, 4326));'''

GET_ZONES = '''SELECT id,name, ST_AsText(area) AS area FROM zones
                JOIN ElementaryGeometries AS e ON (e.f_table_name = 'zones' 
                AND e.origin_rowid = zones.rowid);'''


def create_zone(name,coordinates: List[List[float]])->bool:
    """stores geograhic area of a zone.
    Needs at least 3 coordinates to create a zone.

    Args:
        name (str): name of the zone.
        coordinates (List[tuple[float,float]]): A list containing at least 3 tuples with coordinates that mark the edge of the area.

    Returns:
        bool: Wether the zone could be created or not.
    """
    if len(coordinates) < 3:#at least 3 coordinates are needed.
        return False
    polygon_wkt = coordinates_to_polygon(coordinates)
    inserted_id = db.insert(CREATE_ENTRY,(name,polygon_wkt))
    if inserted_id:
        return True
    return False

def get_zone_of_coordinate(long,lat) -> Zone | None:
    """fetch the zone, the described point is in.

    Args:
        long (_type_): longitude of the point.
        lat (_type_): latitude of the point.

    Returns:
        Zone | None: the Zone if the point is inside a zones area, None if not.
    """
    fetched_zone = db.fetch_one(GET_ZONE,(long,lat))
    return get_obj_from_fetched(fetched_zone)

def get_zones() -> List[Zone]:
    """get a list of all zones.

    Returns:
        List[Zone]: list containing Zone obj.
    """
    fetched_zones = db.fetch_all(GET_ZONES)
    if fetched_zones:
        output = []
        for zone in fetched_zones:
            zone_obj = get_obj_from_fetched(zone)
            if zone_obj:
                output.append(zone_obj)
        return output
    return None

def get_obj_from_fetched(fetched_zone) -> Zone | None:
    """generate Zone obj from fetched element.

    Args:
        fetched_zone (list): fetched attributes from zone.

    Returns:
        Zone | None: zone object or None if obj cant be generated.
    """
    if fetched_match_class(Zone,fetched_zone,3):
        coord_array = spatiapoly_to_long_lat_arr(fetched_zone[2])
        events = get_drone_events_in_zone(fetched_zone[2])
        firerisk = 20
        for event in events:#TODO feuer und rauch unterschiedlich bewerten.
            if firerisk < event.confidence:
                firerisk = event.confidence

        firerisk = firerisk/100*5
        firerisk = round(firerisk)
        firerisk_enum = FireRisk(firerisk)

        zone_obj = Zone(
            id = fetched_zone[0],
            name=fetched_zone[1],
            coordinates=coord_array,
            events=events,
            fire_risk=firerisk_enum
        )
        return zone_obj
    return None

