import datetime
from typing import List
from api.dependencies.classes import DroneUpdate
from database.database import fetched_match_class
import database.database as db


CREATE_DRONE_DATA_TABLE = '''CREATE TABLE drone_data
(
drone_id       integer NOT NULL ,
timestamp    timestamp NOT NULL ,
flight_range   real,
flight_time    real,
PRIMARY KEY (drone_id, timestamp),
FOREIGN KEY (drone_id) REFERENCES drones (id)
);

CREATE INDEX drone_data_FK_1 ON drone_data (drone_id);
SELECT AddGeometryColumn('drone_data', 'coordinates', 4326, 'POINT', 'XY');'''

CREATE_ENTRY = '''INSERT INTO drone_data
                (drone_id,
                timestamp,
                coordinates,
                flight_range,
                flight_time) 
                VALUES (? ,?,MakePoint(?, ?, 4326) ,? ,?);'''
GET_ENTRYS_BY_TIMESTAMP = '''SELECT
                            drone_id,
                            timestamp,
                            flight_range,
                            flight_time,
                            X(coordinates),
                            Y(coordinates)
                            FROM drone_data 
                            WHERE drone_id = ?
                            AND timestamp > ?
                            AND timestamp < ?;'''

GET_ENTRY ='SELECT * FROM drone_data WHERE drone_id = ?;'

GET_UPDATE_IN_ZONE = '''
SELECT drone_id,timestamp,flight_range,flight_time, X(coordinates), Y(coordinates)
FROM drone_data
WHERE ST_Intersects(drone_data.coordinates, GeomFromGeoJSON(?)) 
AND timestamp > ? AND timestamp < ?
ORDER BY timestamp DESC;'''

ACTIVE_DRONES = ''' SELECT DISTINCT	drone_id
                    FROM drone_data
                    WHERE ST_Intersects(drone_data.coordinates, GeomFromGeoJSON(?))
                    AND timestamp > ?;'''


def create_drone_update(drone_id:int,
                            timestamp:datetime.datetime,
                            longitude:float,
                            latitude:float,
                            flight_range:int|None,
                            flight_time:int|None)-> bool:
    """store the data sent by the drone.

    Args:
        drone_id (int): id of the drone.
        timestamp (datetime.datetime): datime timestamp of the event.
        longitude (float): longitute of the update's location.
        latitude (float): latitude of the update's location.
        flight_range (int | None): flight range of the aerial vehicle left in [km].
        flight_time (int | None): flight time of the aerial vehicle left in [minutes].

    Returns:
        bool: True for success, False if something went wrong.
    """
    inserted_id = db.insert(CREATE_ENTRY,
                                (
                                drone_id,
                                timestamp,
                                longitude,
                                latitude,
                                flight_range,
                                flight_time
                                )
                            )
    if inserted_id:
        return True
    return False

def get_drone_data_by_timestamp(drone_id:int,
                                after:datetime.datetime=datetime.datetime.min,
                                before:datetime.datetime=datetime.datetime.max
                                ) -> List[DroneUpdate]:
    """fetches all entrys that are within the choosen timeframe.
    If only drone_id is set, every entry will be fetched.

    Args:
        drone_id (int): _description_
        after (datetime.datetime): fetches everything after this date (not included)
        before (datetime.datetime): fetches everything before this date (not included)

    Returns:
        List[DroneData]: List with the fetched data.
    """
    fetched_data = db.fetch_all(GET_ENTRYS_BY_TIMESTAMP,(drone_id,after,before))

    output = []
    for drone_data in fetched_data:
        dronedata_obj = get_obj_from_fetched(drone_data)
        if dronedata_obj:
            output.append(dronedata_obj)
    return output

def get_latest_update(drone_id:int) -> DroneUpdate:
    """get the latest update of this drone.

    Args:
        drone_id (int): id of the drone.

    Returns:
        DroneUpdate
    """
    fetched_data = db.fetch_one(GET_ENTRY,(drone_id,))
    return get_obj_from_fetched(fetched_data)

def get_updates_in_zone(polygon: str,
                        after: datetime.datetime = datetime.datetime.min,
                        before: datetime.datetime = datetime.datetime.max
                        ) -> List[DroneUpdate]:
    """fetches all entrys that are within the choosen polygon.
    Args:
        polygon (str): polygon str od the area for which the events should be shown
        after (datetime.datetime): fetches everything after this date (not included)
        before (datetime.datetime): fetches everything before this date (not included)

    Returns:
        List[DroneData]: List with the fetched data.
    """
    fetched_data = db.fetch_all(GET_UPDATE_IN_ZONE, (polygon, after, before))
    output = []
    if not fetched_data:
        return None
    for drone_data in fetched_data:
        dronedata_obj = get_obj_from_fetched(drone_data)
        if dronedata_obj:
            output.append(dronedata_obj)
    return output

def get_lastest_update_in_zone(polygon: str) -> DroneUpdate | None:
    """fetches the latest update within the provided polygon area.
    Args:
        polygon (str): geojson polygon str od the area for which the events should be shown

    Returns:
        DroneData: latest update.
    """
    fetched_data = db.fetch_one(GET_UPDATE_IN_ZONE,
                                    (
                                        polygon,
                                        datetime.datetime.min,
                                        datetime.datetime.utcnow()
                                    )
                                )
    return get_obj_from_fetched(fetched_data)

def get_active_drones(polygon: str,
                      after: datetime.datetime = None) -> List[int]:
    """fetched the ids of all active drones in this zone.

    Args:
        polygon (str): _description_
        after (datetime.datetime, optional): _description_. Defaults to now - 1 hour.

    Returns:
        List[int]: _description_
    """
    if after is None:
        after = datetime.datetime.utcnow() - datetime.timedelta(hours=1)
    return db.fetch_all(ACTIVE_DRONES,(polygon,after))


def get_obj_from_fetched(fetched_dronedata) -> DroneUpdate| None:
    """generating DroneUpdate object with the fetched data.

    Args:
        fetched_dronedata: the fetched data from the sqlite cursor.

    Returns:
        DroneData| None: the generated object.
    """
    if fetched_match_class(DroneUpdate,fetched_dronedata):
        try:
            longitude=float(fetched_dronedata[4])
            latitude= float(fetched_dronedata[5])
        except ValueError as exception:
            print(exception)
            longitude, latitude= None, None

        drone_data_obj = DroneUpdate(
            drone_id = fetched_dronedata[0],
            timestamp = fetched_dronedata[1],
            longitude = longitude,
            latitude = latitude,
            flight_range = fetched_dronedata[2],
            flight_time = fetched_dronedata[3]
        )
        return drone_data_obj
    return None