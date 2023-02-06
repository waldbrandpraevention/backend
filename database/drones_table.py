from typing import List

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
type           text,
flight_range   real,
cc_range       real,
flight_time    real,
PRIMARY KEY (id)
);'''

CREATE_DRONE = '''  INSERT INTO drones (name,type,flight_range,cc_range,flight_time)
                    VALUES (? ,? ,? ,? ,?);'''
GET_DRONE = '''SELECT
drones.id, 
drones.name, 
drones.type, 
drones.flight_range, 
drones.cc_range, 
drones.flight_time, 
zones.id
FROM drones
JOIN drone_data ON drone_data.drone_id = drones.id
JOIN zones ON ST_Intersects(drone_data.coordinates, zones.area)
JOIN organization_zones ON organization_zones.zone_id = zones.id
WHERE drones.id=?
AND organization_zones.orga_id = ?
Group by drones.id
Order by drone_data.timestamp;'''

GET_DRONES = '''SELECT
drones.id, 
drones.name, 
drones.type, 
drones.flight_range, 
drones.cc_range, 
drones.flight_time, 
zones.id
FROM drones
JOIN drone_data ON drone_data.drone_id = drones.id
JOIN zones ON ST_Intersects(drone_data.coordinates, zones.area)
JOIN organization_zones ON organization_zones.zone_id = zones.id
WHERE organization_zones.orga_id = ?
Group by drones.id
Order by drone_data.timestamp;'''

def create_drone(name:str,
                 drone_type:str|None,
                 flight_range:int|None,
                 cc_range:int|None,
                 flight_time:int|None):
    """Create an entry for a drone.

    Args:
        name (str): name of the drone
        type (str | None): type of the aerial vehicle
        flight_range (int | None): maximum flight range of the aerial vehicle in [km]
        cc_range (int | None): maximum command and control range of the aerial vehicle in [km]
        flight_time (int | None): maximum flight time of the aerial vehicle in [minutes]

    Returns:
        Drone: obj of the drone.
    """
    inserted_id = db.insert(CREATE_DRONE,
                                (
                                    name,
                                    drone_type,
                                    flight_range,
                                    cc_range,
                                    flight_time
                                )
                             )
    if inserted_id:
        drone_obj = Drone(
        id = inserted_id,
        name=name,
        type=drone_type,
        flight_range=flight_range,
        cc_range=cc_range,
        flight_time=flight_time
        )
        return drone_obj
    return None

def get_drone(drone_id:int,orga_id:int)-> Drone | None:
    """get the requested drone.

    Args:
        name (str): name of that drone.

    Returns:
        Drone | None: the drone obj or None if not found.
    """
    fetched_drone = db.fetch_one(GET_DRONE,(drone_id,orga_id))
    return get_obj_from_fetched(fetched_drone)

def get_drones(orga_id:int) -> List[Drone]:
    """fetches all stored drones.

    Returns:
        List[Drone]: list of all stored drones.
    """
    fetched_drones = db.fetch_all(GET_DRONES,(orga_id,))
    if fetched_drones is None:
        return None
    output = []
    for drone in fetched_drones:
        drone_obj = get_obj_from_fetched(drone)
        if drone_obj:
            output.append(drone_obj)
    return output

def get_all_drones() -> List[Drone]:
    """fetches all stored drones.

    Returns:
        List[Drone]: list of all stored drones.
    """
    fetched_drones = db.fetch_all(GET_DRONES)
    if fetched_drones is None:
        return None
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
    if fetched_match_class(Drone,fetched_drone,1):
        try:
            drone_obj = Drone(
                id = fetched_drone[0],
                name=fetched_drone[1],
                type=fetched_drone[2],
                flight_range=fetched_drone[3],
                cc_range=fetched_drone[4],
                flight_time=fetched_drone[5],
                zone_id=fetched_drone[6]
            )
            return drone_obj
        except ValueError as exception:
            print(exception)

    return None
