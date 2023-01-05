

import sqlite3
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


def create_zone(name,x1,y1,x2,y2,x3,y3,x4,y4):
    try:
        with database_connection() as conn:
            cursor = conn.cursor()
            point_wkt = 'POLYGON(({0} {1},{2} {3},{4} {5},{6} {7}))'.format(x1,y1,x2,y2,x3,y3,x4,y4)
            cursor.execute(CREATE_ENTRY,(name,point_wkt))
            conn.commit()
            cursor.close()
            return True
    except sqlite3.IntegrityError as e:##TODO
        print(e)
    return False

def get_zone(long,lat):
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

