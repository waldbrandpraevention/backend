"""funcs to read and write on the drone_event table in database."""
import datetime
import random
from typing import List
from api.dependencies.classes import DroneEvent, EventType, FireRisk
from database.database import fetched_match_class
import database.database as db
from database import drone_updates_table

CREATE_DRONE_EVENT_TABLE = '''CREATE TABLE drone_event
(
drone_id       integer NOT NULL ,
timestamp    timestamp NOT NULL ,
event_type   integer NOT NULL,
confidence   integer NOT NULL,
picture_path   text,
csv_file_path  text ,
PRIMARY KEY (drone_id, timestamp),
FOREIGN KEY (drone_id) REFERENCES drones (id)
);

CREATE INDEX drone_event_FK_1 ON drone_event (drone_id);
SELECT AddGeometryColumn('drone_event', 'coordinates', 4326, 'POINT', 'XY');'''

CREATE_ENTRY = '''
INSERT INTO drone_event (drone_id,timestamp,coordinates,event_type,confidence,picture_path,csv_file_path) 
VALUES (? ,?,MakePoint(?, ?, 4326)  ,? ,?,?,?);'''
GET_ENTRYS_BY_TIMESTAMP = '''
SELECT drone_id,timestamp, X(coordinates), Y(coordinates),event_type,confidence,picture_path,csv_file_path
FROM drone_event 
WHERE drone_id = ? AND timestamp > ? AND timestamp < ?;'''
GET_ENTRY = ''' SELECT * FROM drone_event WHERE drone_id = ?
                ORDER BY timestamp DESC;'''

GET_EVENT_IN_ZONE = '''
SELECT drone_id,timestamp, X(coordinates), Y(coordinates),event_type,confidence,picture_path,csv_file_path
FROM drone_event
WHERE ST_Intersects(drone_event.coordinates, GeomFromGeoJSON(?)) 
AND timestamp > ? AND timestamp < ?;'''


def insert_demo_events(long: float, lat: float, droneid = 1):
    """insert 5 demo drone events.

    Args:
        long (float): long of the coordinate.
        lat (float): lat of the coordinate.
    """
    updates = drone_updates_table.get_drone_data_by_timestamp(droneid)
    if updates is not None and len(updates)>0:
        print('already created drone events.')
        return
    timestamp = datetime.datetime.utcnow()
    i = 0
    num_inserted = 0
    flight_range = 100
    flight_time =0
    while num_inserted < 4:
        event_rand = random.randint(0, 2)
        long_rand = random.randint(0, 100)/1000000
        lat_rand = random.randint(0, 100)/1000000
        long= long+long_rand
        lat = lat+lat_rand
        flight_range-=2
        flight_time+=10
        drone_updates_table.create_drone_update(
            drone_id=droneid,
            timestamp=timestamp,
            longitude=long,
            latitude=lat,
            flight_range=flight_range,
            flight_time=flight_time
        )
        if event_rand > 0:
            confidence = random.randint(20, 90)
            
            create_drone_event_entry(
                drone_id=droneid,
                timestamp=timestamp,
                longitude=long,
                latitude=lat,
                event_type=event_rand,
                confidence=confidence,
                picture_path=f'demo/path/{i}',
                csv_file_path=f'demo/path/{i}'
            )
            num_inserted += 1
        timestamp += datetime.timedelta(seconds=10)
        i += 1


def create_drone_event_entry(drone_id: int,
                             timestamp: datetime.datetime,
                             longitude: float,
                             latitude: float,
                             event_type: int,
                             confidence: int,
                             picture_path: str | None,
                             csv_file_path: str | None) -> bool:
    """store the data sent by the drone.

    Args:
        drone_id (int): id of the drone.
        timestamp (datetime.datetime): datime timestamp of the event.
        longitude (float): longitute of the event's location.
        latitude (float): latitude of the event's location.
        picture_path (str | None): path to the folder containing the events pictures.
        csv_file_path (str | None): path to the folder containing the events csv files.

    Returns:
        bool: True for success, False if something went wrong.
    """

    inserted_id = db.insert(CREATE_ENTRY,
                            (drone_id,
                            timestamp,
                            longitude,
                            latitude,
                            event_type,
                            confidence,
                            picture_path,
                            csv_file_path))
    if inserted_id:
        return True
    return False


def get_drone_event_by_timestamp(drone_id: int,
                                 after: datetime.datetime = datetime.datetime.min,
                                 before: datetime.datetime = datetime.datetime.max
                                 ) -> List[DroneEvent]:
    """fetches all entrys that are within the choosen timeframe.
    If only drone_id is set, every entry will be fetched.

    Args:
        drone_id (int): the id of the drone.
        after (datetime.datetime): fetches everything after this date (not included)
        before (datetime.datetime): fetches everything before this date (not included)

    Returns:
        List[DroneData]: List with the fetched data.
    """
    fetched_data = db.fetch_all(
        GET_ENTRYS_BY_TIMESTAMP, (drone_id, after, before))
    output = []
    for drone_data in fetched_data:
        dronedata_obj = get_obj_from_fetched(drone_data)
        if dronedata_obj:
            output.append(dronedata_obj)
    return output


def get_drone_events_in_zone(polygon: str,
                             after: datetime.datetime = datetime.datetime.max,
                             before: datetime.datetime = datetime.datetime.max
                             ) -> List[DroneEvent]:
    """fetches all entrys that are within the choosen polygon.
    Args:
        polygon (str): polygon str od the area for which the events should be shown
        after (datetime.datetime): fetches everything after this date (not included)
        before (datetime.datetime): fetches everything before this date (not included)

    Returns:
        List[DroneData]: List with the fetched data.
    """
    fetched_data = db.fetch_all(GET_EVENT_IN_ZONE, (polygon, after, before))
    output = []
    if not fetched_data:
        return None
    for drone_data in fetched_data:
        dronedata_obj = get_obj_from_fetched(drone_data)
        if dronedata_obj:
            output.append(dronedata_obj)
    return output


def get_latest_event(drone_id: int) -> DroneEvent:
    """fetch latest event, this dron has recorded.

    Args:
        drone_id (int): id of the drone.

    Returns:
        DroneEvent
    """
    fetched_data = db.fetch_one(GET_ENTRY, (drone_id,))
    if fetched_data:
        return get_obj_from_fetched(fetched_data)
    return None


def get_obj_from_fetched(fetched_dronedata) -> DroneEvent | None:
    """generating DroneData objects with the fetched data.

    Args:
        fetched_dronedata: the fetched data from the sqlite cursor.

    Returns:
        DroneData| None: the generated object.
    """
    if fetched_match_class(DroneEvent, fetched_dronedata):

        try:
            longitude = float(fetched_dronedata[2])
            latitude = float(fetched_dronedata[3])
        except ValueError:
            longitude, latitude = None, None

        try:
            eventtype = EventType(fetched_dronedata[4])
        except ValueError:
            eventtype = None

        drone_data_obj = DroneEvent(
            drone_id=fetched_dronedata[0],
            timestamp=fetched_dronedata[1],
            longitude=longitude,
            latitude=latitude,
            event_type=eventtype,
            confidence=fetched_dronedata[5],
            picture_path=fetched_dronedata[6],
            csv_file_path=fetched_dronedata[7]
        )
        return drone_data_obj
    return None


def calculate_firerisk(events: List[DroneEvent]) -> FireRisk:
    """calculates the firerisk, based on the events fire/smoke confidences.

    Args:
        events (List[DroneEvent]): list of drone events.

    Returns:
        FireRisk: the calculated risk.
    """
    firerisk = 20
    for event in events:  # TODO feuer und rauch unterschiedlich bewerten.
        if firerisk < event.confidence:
            firerisk = event.confidence

    firerisk = firerisk/100*5
    firerisk = round(firerisk)
    return FireRisk(firerisk)
