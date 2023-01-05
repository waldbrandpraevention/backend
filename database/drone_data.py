import datetime
from enum import Enum
import json
import sqlite3
from typing import List
from api.dependencies.classes import DroneData
from database.database import database_connection, fetched_match_class
from database.spatia import spatiapoint_to_long_lat


CREATE_DRONE_DATA_TABLE = '''CREATE TABLE drone_data
(
drone_id       integer NOT NULL ,
timestamp    timestamp NOT NULL ,
picture_path   text NOT NULL ,
ai_predictions json ,
csv_file_path  text ,
PRIMARY KEY (drone_id, timestamp),
FOREIGN KEY (drone_id) REFERENCES drones (id)
);

CREATE INDEX drone_data_FK_1 ON drone_data (drone_id);
SELECT AddGeometryColumn('drone_data', 'geometry', 4326, 'POINT', 'XY');'''
# zone_id        integer NOT NULL ,
# FOREIGN KEY (zone_id) REFERENCES Zones (id),
# CREATE INDEX drone_data_FK_1 ON drone_data (zone_id);
CREATE_ENTRY = 'INSERT INTO drone_data (drone_id,timestamp,geometry,picture_path,ai_predictions,csv_file_path) VALUES (? ,?,GeomFromText(?, 4326) ,? ,?,?);'
GET_ENTRYS_BY_TIMESTAMP = 'SELECT *, ST_AsText(geometry) AS geo FROM drone_data WHERE drone_id = ? AND timestamp > ? AND timestamp < ?;'
GET_ENTRY ='SELECT * FROM drone_data WHERE drone_id = ?;'



def create_drone_zone_entry(drone_id:int,
                            timestamp:datetime.datetime,
                            longitude:float,
                            latitude:float,
                            picture_path:str|None,
                            ai_predictions:dict|None,
                            csv_file_path:str|None)-> bool:
    """store the data sent by the drone.

    Args:
        drone_id (int): _description_
        timestamp (datetime.datetime): _description_
        longitude (float): _description_
        latitude (float): _description_
        picture_path (str | None): _description_
        ai_predictions (dict | None): _description_
        csv_file_path (str | None): _description_

    Returns:
        bool: True for success, False if something went wrong.
    """
    try:
        with database_connection() as conn:
            cursor = conn.cursor()
            point_wkt = 'POINT({0} {1})'.format(longitude, latitude)
            cursor.execute(CREATE_ENTRY,(drone_id,timestamp,point_wkt,picture_path,json.dumps(ai_predictions),csv_file_path))
            conn.commit()
            cursor.close()
            return True
    except sqlite3.IntegrityError as e:##TODO
        print(e)
    return False

def get_drone_data_by_timestamp(drone_id:int,after:datetime.datetime=datetime.datetime.min,before:datetime.datetime=datetime.datetime.max) -> List[DroneData]:
    """fetches all entrys that are within the choosen timeframe.
    If only drone_id is set, every entry will be fetched.

    Args:
        drone_id (int): _description_
        after (datetime.datetime): fetches everything after this date (not included)
        before (datetime.datetime): fetches everything before this date (not included)

    Returns:
        List[DroneData]: List with the fetched data.
    """
    try:
        with database_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(GET_ENTRYS_BY_TIMESTAMP,(drone_id,after,before))
            fetched_data = cursor.fetchall()
            cursor.close()
            output = []
            for drone_data in fetched_data:
                dronedata_obj = get_obj_from_fetched(drone_data)
                if dronedata_obj:
                    output.append(dronedata_obj)
            return output
    except sqlite3.IntegrityError as e:##TODO
        print(e)

def get_latest_by_timestamp(drone_id:int) -> DroneData:
    
    try:
        with database_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(GET_ENTRY,(drone_id,))
            fetched_data = cursor.fetchone()
            cursor.close()
            if fetched_data:
                dronedata_obj = get_obj_from_fetched(fetched_data)
            else:
                dronedata_obj = None
                
            return dronedata_obj
    except sqlite3.IntegrityError as e:##TODO
        print(e)


def get_obj_from_fetched(fetched_dronedata) -> DroneData| None:
    """generating DroneData objects with the fetched data.

    Args:
        fetched_dronedata: the fetched data from the sqlite cursor.

    Returns:
        DroneData| None: the generated object.
    """
    if fetched_match_class(DroneData,fetched_dronedata):
        try:
            ai_predictions = json.loads(fetched_dronedata[3])
        except:
            print('json loads error')
            ai_predictions = None

        try:
            longitude, latitude= spatiapoint_to_long_lat(fetched_dronedata[6])
        except Exception as e:
            print(e)
            longitude, latitude= None, None

        drone_data_obj = DroneData(
            drone_id = fetched_dronedata[0],
            timestamp = fetched_dronedata[1],
            longitude = longitude,
            latitude = latitude,
            picture_path = fetched_dronedata[2],
            ai_predictions = ai_predictions,
            csv_file_path = fetched_dronedata[4],
        )
        return drone_data_obj
    return None