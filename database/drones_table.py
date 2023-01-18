from typing import List
from enum import Enum

from api.dependencies.classes import Drone
from database.database import fetched_match_class
import database.database as db

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
        Drone: obj of the drone.
    """
    inserted_id = db.insert(CREATE_DRONE,(name,droneowner_id,type,flight_range,cc_range,flight_time))
    if inserted_id:
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
    return None

def get_drone(name:str)-> Drone | None:
    """get the requested drone.

    Args:
        name (str): name of that drone.

    Returns:
        Drone | None: the drone obj or None if not found.
    """
    fetched_drone = db.fetch_one(GET_DRONE,(name,))
    return get_obj_from_fetched(fetched_drone)

def get_drones() -> List[Drone]:
    """fetches all stored drones.

    Returns:
        List[Drone]: list of all stored drones.
    """
    fetched_drones = db.fetch_all('SELECT * FROM drones')
    output = []
    for drone in fetched_drones:
        drone_obj = get_obj_from_fetched(drone)
        if drone_obj:
            output.append(drone_obj)
    return output

def get_obj_from_fetched(fetched_drone):
    """generate Drone obj from fetched element.

    Args:
        fetched_drone (list): fetched attributes from drone.

    Returns:
        Drone: drone object.
    """
    if fetched_match_class(Drone,fetched_drone,2):
        try:
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
        except Exception as exception:
            print(exception)

    return None
