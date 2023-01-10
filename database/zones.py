

import sqlite3
from typing import List
from database.database import database_connection

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
GET_ZONE = 'SELECT id,name FROM zones WHERE ST_Intersects(area, GeomFromText(?, 4326));'


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
            point_wkt = 'POINT({0} {1})'.format(long, lat)
            cursor.execute(GET_ZONE,(point_wkt,))
            fetched_data = cursor.fetchone()
            cursor.close()
            if fetched_data:
                return True
            else:
                return False
                
    except sqlite3.IntegrityError as e:##TODO
        print(e)
    return False

