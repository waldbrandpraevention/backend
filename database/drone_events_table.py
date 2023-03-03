"""funcs to read and write on the drone_event table in database."""
import datetime
import random
from typing import List
from api.dependencies.classes import DroneEvent, EventType, FireRisk
from database.database import fetched_match_class
import database.database as db
from database import drone_updates_table

EVENT_ID = 'id'
DRONE_ID = 'drone_id'
TIMESTAMP = 'timestamp'
EVENT_TYPE = 'event_type'
CONFIDENCE = 'confidence'
PICTURE_PATH='picture_path'
CSV_FILE_PATH= 'csv_file_path'
COORDINATES= 'coordinates'

CREATE_DRONE_EVENT_TABLE = f'''CREATE TABLE drone_event
(
{EVENT_ID}     integer NOT NULL ,
{DRONE_ID}     integer NOT NULL ,
{TIMESTAMP}    timestamp NOT NULL ,
{EVENT_TYPE}   integer NOT NULL,
{CONFIDENCE}   integer NOT NULL,
{PICTURE_PATH}   text,
{CSV_FILE_PATH}  text ,
PRIMARY KEY ({EVENT_ID}),
FOREIGN KEY ({DRONE_ID}) REFERENCES drones (id)
);

CREATE INDEX drone_event_FK_1 ON drone_event ({DRONE_ID});
SELECT AddGeometryColumn('drone_event', '{COORDINATES}', 4326, 'POINT', 'XY');'''

CREATE_ENTRY = '''
INSERT INTO drone_event (drone_id,timestamp,coordinates,event_type,confidence,picture_path,csv_file_path) 
VALUES (? ,?,MakePoint(?, ?, 4326)  ,? ,?,?,?);'''

GET_ENfTRY = '''
SELECT drone_event.id, drone_id,timestamp, X(coordinates), Y(coordinates),event_type,confidence,picture_path,csv_file_path, zones.id
FROM drone_event
LEFT JOIN zones ON ST_Intersects(zones.area, coordinates)
{}
ORDER BY timestamp DESC;'''

GET_EVENT_IN_ZONE = '''
SELECT drone_event.id,drone_id,timestamp, X(coordinates), Y(coordinates),event_type,confidence,picture_path,csv_file_path, zones.id
FROM drone_event
JOIN zones ON ST_Intersects(zones.area, coordinates)
AND timestamp > ? AND timestamp < ?;'''

GET_EVENT_BY_ID = '''
SELECT drone_event.id,drone_id,timestamp, X(coordinates), Y(coordinates),event_type,confidence,picture_path,csv_file_path, zones.id
FROM drone_event
JOIN zones ON ST_Intersects(zones.area, coordinates)
AND drone_event.id = ?;'''


def insert_demo_events(long: float, lat: float, droneid = 1):
    """insert 5 demo drone events.

    Args:
        long (float): long of the coordinate.
        lat (float): lat of the coordinate.
    """
    update = drone_updates_table.get_latest_update(droneid)
    if update is not None:
        print('already created drone events.')
        return
    timestamp = datetime.datetime.utcnow()
    i = 0
    num_inserted = 0
    flight_range = 100
    flight_time =0
    while num_inserted < 4:
        event_rand = random.randint(0, 2)
        long_rand = random.randint(0, 100)/100000
        lat_rand = random.randint(0, 100)/100000
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
    if inserted_id is not None:
        return True
    return False


def get_event_by_id(event_id: int) -> DroneEvent | None:
    """get the requested drone just by the id

    Args:
        name (str): name of that drone.

    Returns:
        Drone | None: the drone obj or None if not found.
    """
    fetched_event = db.fetch_one(GET_EVENT_BY_ID, (event_id,))
    return get_obj_from_fetched(fetched_event)

def get_drone_event(drone_id: int = None,
                    polygon: str=None,
                    after: datetime.datetime = None,
                    before: datetime.datetime = None
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
    sql_arr, tuple_arr = drone_updates_table.gernerate_drone_sql(polygon, drone_id, after, before)

    sql = db.add_where_clause(GET_ENTRY, sql_arr)

    fetched_data = db.fetch_all(
        sql, tuple(tuple_arr)
        )

    if fetched_data is None:
        return None

    output = []
    for drone_event in fetched_data:
        droneevent_obj = get_obj_from_fetched(drone_event)
        if droneevent_obj:
            output.append(droneevent_obj)
    return output

def get_obj_from_fetched(fetched_dronedata) -> DroneEvent | None:
    """generating DroneData objects with the fetched data.

    Args:
        fetched_dronedata: the fetched data from the sqlite cursor.

    Returns:
        DroneData| None: the generated object.
    """
    if fetched_match_class(DroneEvent, fetched_dronedata):

        try:
            longitude = float(fetched_dronedata[3])
            latitude = float(fetched_dronedata[4])
        except ValueError:
            longitude, latitude = None, None

        try:
            eventtype = EventType(fetched_dronedata[5])
        except ValueError:
            eventtype = None

        drone_data_obj = DroneEvent(
            id=fetched_dronedata[0],
            drone_id=fetched_dronedata[1],
            timestamp=fetched_dronedata[2],
            lon =longitude,
            lat =latitude,
            event_type=eventtype,
            confidence=fetched_dronedata[6],
            picture_path=fetched_dronedata[7],
            csv_file_path=fetched_dronedata[8],
            zone_id=fetched_dronedata[9]
        )
        return drone_data_obj
    return None


def calculate_firerisk(events: List[DroneEvent]) -> tuple[FireRisk,FireRisk,FireRisk]:
    """calculates the firerisk, based on the events fire/smoke confidences.
    sehr niedrig rauch:>5 feuer: >0
    niedrig rauch:>40 feuer: > 10
    mittel rauch:>60 feuer: >30
    hoch rauch:>80 feuer: >70
    sehr hoch rauch:>... feuer: >90
    Args:
        events (List[DroneEvent]): list of drone events.

    Returns:
        FireRisk: the calculated risk.
    """
    smokerisk= 0
    firerisk = 0
    for event in events:
        if event.event_type == EventType.SMOKE:
            if smokerisk < event.confidence:
                smokerisk = event.confidence
        else:
            if firerisk < event.confidence:
                firerisk = event.confidence

    try:
        calculated_enum = round(smokerisk/100 * 5)
        if calculated_enum > 5:
            calculated_enum = 5
        elif calculated_enum < 1:
            calculated_enum = 1
        smoke_risk = FireRisk(calculated_enum)
    except TypeError:
        smoke_risk = None

    try:
        calculated_enum = round(firerisk/100 * 5)
        if calculated_enum > 5:
            calculated_enum = 5
        elif calculated_enum < 1:
            calculated_enum = 1
        fire_risk = FireRisk(calculated_enum)
    except TypeError:
        fire_risk = None

    if smokerisk > 90 or firerisk > 90:
        return FireRisk.VERY_HEIGH, smoke_risk, fire_risk

    if smokerisk > 80 or firerisk > 70:
        return FireRisk.HEIGH, smoke_risk, fire_risk

    if smokerisk > 60 or firerisk > 30:
        return FireRisk.MIDDLE, smoke_risk, fire_risk

    if smokerisk > 40 or firerisk > 10:
        return FireRisk.LOW, smoke_risk, fire_risk

    return FireRisk.VERY_LOW, smoke_risk, fire_risk
