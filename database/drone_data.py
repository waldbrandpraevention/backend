import datetime
from enum import Enum
import json
import sqlite3
from api.dependencies.classes import DroneData
from database.database import database_connection, fetched_match_class


CREATE_DRONE_DATA_TABLE = '''CREATE TABLE drone_data
(
drone_id       integer NOT NULL ,
timestamp    timestamp NOT NULL ,
longitude    text NOT NULL,
latitude     text NOT NULL,
picture_path   text NOT NULL ,
ai_predictions json ,
csv_file_path  text ,
PRIMARY KEY (drone_id, timestamp),
FOREIGN KEY (drone_id) REFERENCES drones (id)
);

CREATE INDEX drone_data_FK_1 ON drone_data (drone_id);'''
# zone_id        integer NOT NULL ,
# FOREIGN KEY (zone_id) REFERENCES Zones (id),
# CREATE INDEX drone_data_FK_1 ON drone_data (zone_id);
CREATE_ENTRY = 'INSERT INTO drone_data (drone_id,timestamp,longitude,latitude,picture_path,ai_predictions,csv_file_path) VALUES (? ,?,?,? ,? ,?,?);'
GET_ENTRYS_BY_TIMESTAMP = 'SELECT * FROM drone_data WHERE drone_id = ? AND timestamp > ?;'


def create_drone_zone_entry(drone_id:int,
                            timestamp:datetime.datetime,
                            longitude:float,
                            latitude:float,
                            picture_path:str|None,
                            ai_predictions:dict|None,
                            csv_file_path:str|None):
    
    try:
        with database_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(CREATE_ENTRY,(drone_id,timestamp,str(longitude),str(latitude),picture_path,json.dumps(ai_predictions),csv_file_path))
            conn.commit()
            cursor.close()
        
    except sqlite3.IntegrityError as e:##TODO
        print(e)
    return None

def get_drone_data_by_timestamp(drone_id:int,since_timestamp:datetime.datetime):

    try:
        with database_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(GET_ENTRYS_BY_TIMESTAMP,(drone_id,since_timestamp))
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


def get_obj_from_fetched(fetched_dronedata):

    if fetched_match_class(DroneData,fetched_dronedata):
        try:
            ai_predictions = json.loads(fetched_dronedata[5])
        except:
            print('json loads error')
            ai_predictions = None
        drone_data_obj = DroneData(
            drone_id = fetched_dronedata[0],
            timestamp = fetched_dronedata[1],
            longitude = float(fetched_dronedata[2]),
            latitude = float(fetched_dronedata[3]),
            picture_path = fetched_dronedata[4],
            ai_predictions = ai_predictions,
            csv_file_path = fetched_dronedata[6],
        )
        return drone_data_obj
    return None