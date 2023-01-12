

import sqlite3
from typing import List
from api.dependencies.classes import FireRisk, Zone
from database.database import database_connection, fetched_match_class
from database.spatia import spatiapoly_to_long_lat_arr
from database.drone_events_table import get_drone_events_in_zone

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


def create_zone(name,coordinates: List[tuple[float,float]])->bool:
    """stores geograhic area of a zone.
    Needs at least 3 coordinates to create a zone.

    Args:
        name (str): name of the zone.
        coordinates (List[tuple[float,float]]): A list containing at least 3 tuples with coordinates that mark the edge of the area.

    Returns:
        bool: Wether the zone could be created or not.
    """
    try:
        if len(coordinates) < 3:#at least 3 coordinates are needed.
            return False
        first_coordinate = coordinates.pop(0)
        polygon_wkt = f'POLYGON(({first_coordinate[0]} {first_coordinate[1]}'
        for coordinate in coordinates:
            polygon_wkt += f',{coordinate[0]} {coordinate[1]}'
        polygon_wkt +='))'
        with database_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(CREATE_ENTRY,(name,polygon_wkt))
            conn.commit()
            cursor.close()
            return True
    except sqlite3.IntegrityError as e:##TODO
        print(e)
    return False

def get_zone_of_coordinate(long,lat):
    """_summary_

    Args:
        long (_type_): _description_
        lat (_type_): _description_

    Returns:
        _type_: _description_
    """
    try:
        with database_connection() as conn:
            cursor = conn.cursor()
            #point_wkt = 'POINT({0} {1})'.format(long, lat) for 
            cursor.execute(GET_ZONE,(long,lat))
            fetched_zone = cursor.fetchone()
            cursor.close()
            zone_obj = get_obj_from_fetched(fetched_zone)
            return zone_obj
                
    except sqlite3.IntegrityError as e:##TODO
        print(e)
    return None

def get_zones():
    """_summary_

    Args:
        long (_type_): _description_
        lat (_type_): _description_

    Returns:
        _type_: _description_
    """
    try:
        with database_connection() as conn:
            cursor = conn.cursor()
            #point_wkt = 'POINT({0} {1})'.format(long, lat) for 
            cursor.execute(GET_ZONES)
            fetched_zone = cursor.fetchall()
            cursor.close()
            output = []
            for zone in fetched_zone:
                zone_obj = get_obj_from_fetched(zone)
                if zone_obj:
                    output.append(zone_obj)
            return output
                
    except sqlite3.IntegrityError as e:##TODO
        print(e)
    return None

def get_obj_from_fetched(fetched_zone):
    """generate Organization obj from fetched element.

    Args:
        fetched_orga (list): fetched attributes from orga.

    Returns:
        Organization: orga object.
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

        orga_obj = Zone(
            id = fetched_zone[0],
            name=fetched_zone[1],
            coordinates=coord_array,
            events=events,
            fire_risk=firerisk_enum
        )
        return orga_obj
    return None

