from typing import List
import datetime
from enum import Enum
import sqlite3

from api.dependencies.classes import Drone
from database.database import database_connection, fetched_match_class

# "name": "name of the aerial vehicle according to manufacturer",
# "type": "type of the aerial vehicle",
# "flight_range": "maximum flight range of the aerial vehicle in [km]",
# "cc_range": "maximum command and control range of the aerial vehicle in [km]",
# "flight_time": "maximum flight time of the aerial vehicle in [minutes]",
# "sensors": "list of attached sensors"

CREATE_DRONES_TABLE = '''CREATE TABLE drones
(
id             integer NOT NULL ,
name           text NOT NULL ,
droneowner_id  integer,
type           text,
flight_range   real,
cc_range       real,
flight_time    real,
PRIMARY KEY (id),
FOREIGN KEY (droneowner_id) REFERENCES drone_owners (id)
);
CREATE UNIQUE INDEX IF NOT EXISTS drones_AK ON drones (name);
CREATE INDEX drones_FK_1 ON drones (droneowner_id);'''

CREATE_DRONE = 'INSERT INTO drones (name,droneowner_id,type,flight_range,cc_range,flight_time) VALUES (? ,? ,? ,? ,? ,?);'
GET_DRONE = 'SELECT * FROM drones WHERE name=?;'

def create_drone(name:str,droneowner_id:int|None,type:str|None,flight_range:int|None,cc_range:int|None,flight_time:int|None):
    """Create an entry for a drone.

    Args:
        name (str): name of the drone.
        droneowner_id (int | None): the drone owners id. 
        type (str | None): type of the aerial vehicle
        flight_range (int | None): maximum flight range of the aerial vehicle in [km]
        cc_range (int | None): maximum command and control range of the aerial vehicle in [km]
        flight_time (int | None): maximum flight time of the aerial vehicle in [minutes]

    Returns:
        Drone: _description_
    """
    try:
        with database_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(CREATE_DRONE,(name,droneowner_id,type,flight_range,cc_range,flight_time))
            inserted_id = cursor.lastrowid
            conn.commit()
            cursor.close()
            drone_obj = Drone(
            id = inserted_id,
            name=name,
            droneowner_id= droneowner_id,
            type=type,
            flight_range=flight_range,
            cc_range=cc_range,
            flight_time=flight_time
        )
        return drone_obj
    except sqlite3.IntegrityError as e:##TODO
        print(e)
    return None

def get_drone(name:str)-> Drone | None:
    """get the requested drone.

    Args:
        name (str): name of that drone.

    Returns:
        Drone | None: the drone obj or None if not found.
    """
    try:
        with database_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(GET_DRONE,(name,))
            fetched_drone = cursor.fetchone()
            cursor.close()
            if fetched_drone:
                drone_obj = get_obj_from_fetched(fetched_drone)
                return drone_obj
    except sqlite3.IntegrityError as e:##TODO
        print(e)

def get_drones() -> List[Drone]:
    """fetches all stored drones.

    Returns:
        List[Drone]: list of all stored drones.
    """
    try:
        with database_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM drones')
            fetched_drones = cursor.fetchall()
            cursor.close()
            output = []
            for drone in fetched_drones:
                drone_obj = get_obj_from_fetched(drone)
                if drone_obj:
                    output.append(drone_obj)
            return output
    except sqlite3.IntegrityError as e:
        print(e)
    return None

def get_obj_from_fetched(fetched_drone):
    """generate Drone obj from fetched element.

    Args:
        fetched_drone (list): fetched attributes from drone.

    Returns:
        Drone: drone object.
    """
       
    drone_obj = Drone(
        id = fetched_drone[0],
        name=fetched_drone[1],
        droneowner_id= fetched_drone[2],
        type=fetched_drone[3],
        flight_range=fetched_drone[4],
        cc_range=fetched_drone[5],
        flight_time=fetched_drone[6]
    )
    return drone_obj
