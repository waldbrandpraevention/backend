"""DB functions for drone updates"""
import datetime
from typing import List
from shapely.geometry import Point, LineString, mapping
from api.dependencies.classes import DroneUpdate, DroneUpdateWithRoute
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

GET_ENTRY ='''SELECT
                drone_id,
                timestamp,
                flight_range,
                flight_time,
                X(coordinates),
                Y(coordinates)
                FROM drone_data 
                {}
                ORDER BY timestamp DESC;'''

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

def get_drone_updates(  polygon:str,
                        drone_id:int=None,
                        after:datetime.datetime=None,
                        before:datetime.datetime=None,
                        get_coords_only:bool = False
                        ) -> List[DroneUpdate] | DroneUpdateWithRoute:
    """fetches all entrys that are within the choosen timeframe.
    If only drone_id is set, every entry will be fetched.

    Args:
        drone_id (int): id of the drone.
        after (datetime.datetime): fetches everything after this date (not included)
        before (datetime.datetime): fetches everything before this date (not included)

    Returns:
        List[DroneData]: List with the fetched data.
    """
    sql_arr, tuple_arr = gernerate_drone_sql(polygon, drone_id, after, before)

    sql = db.add_where_clause(GET_ENTRY, sql_arr)

    fetched_data = db.fetch_all(sql,tuple(tuple_arr))

    if fetched_data is None:
        return None

    output = []
    if get_coords_only:
        return get_routeobj_from_fetched(fetched_data)

    for drone_data in fetched_data:
        dronedata = get_obj_from_fetched(drone_data)
        if dronedata:
            output.append(dronedata)
    return output

def gernerate_drone_sql(polygon:str,
                        drone_id:int,
                        after:datetime.datetime,
                        before:datetime.datetime
                        ):
    """generates the sql and tuple array for the get_drone_updates function.

    Args:
        polygon (str): polygon str od the area for which the events should be shown
        drone_id (int): id of the drone.
        after (datetime.datetime): fetches everything after this date (not included)
        before (datetime.datetime): fetches everything before this date (not included)

    Returns:
        List[str], List[any]: sql array and tuple array
    """

    sql_arr = []
    tuple_arr = []
    if drone_id is not None:
        sql_arr.append(db.create_where_clause_statement('drone_id','='))
        tuple_arr.append(drone_id)

    if polygon is not None:
        sql_arr.append(db.create_intersection_clause('coordinates'))
        tuple_arr.append(polygon)

    if after is not None:
        sql_arr.append(db.create_where_clause_statement('timestamp','>'))
        tuple_arr.append(after)

    if before is not None:
        sql_arr.append(db.create_where_clause_statement('timestamp','<'))
        tuple_arr.append(before)

    return sql_arr, tuple_arr

def get_latest_update(drone_id:int) -> DroneUpdate:
    """get the latest update of this drone.

    Args:
        drone_id (int): id of the drone.

    Returns:
        DroneUpdate
    """
    sql = db.add_where_clause(GET_ENTRY, [db.create_where_clause_statement('drone_id','=')])
    fetched_data = db.fetch_one(sql,(drone_id,))
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
    if fetched_data is None:
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
            lon= longitude,
            lat = latitude,
            flight_range = fetched_dronedata[2],
            flight_time = fetched_dronedata[3]
        )
        return drone_data_obj
    return None

def get_routeobj_from_fetched(fetched_dronedataarr) -> List[DroneUpdate]| None:
    """generating DroneUpdate object with the fetched data.

    Args:
        fetched_dronedata: the fetched data from the sqlite cursor.

    Returns:
        DroneData| None: the generated object.
    """
    if fetched_dronedataarr is None:
        return None

    drones_arr = []
    route_arr = []
    fetched_dronedataarr.sort(key=lambda x: x[0])#TODO sql sort
    drone_update = get_obj_from_fetched(fetched_dronedataarr[0])
    for fetched_dronedata in fetched_dronedataarr:
        if fetched_match_class(DroneUpdate,fetched_dronedata):
            if fetched_dronedata[0] != drone_update.drone_id:
                drones_arr.append(create_drone_with_route(drone_update,route_arr))
                route_arr = []
                drone_update = get_obj_from_fetched(fetched_dronedata)
            else:
                try:
                    longitude=float(fetched_dronedata[4])
                    latitude= float(fetched_dronedata[5])
                    route_arr.append(Point(longitude, latitude))
                except ValueError as exception:
                    print(exception)

    drones_arr.append(create_drone_with_route(drone_update,route_arr))
    return drones_arr

def create_drone_with_route(drone_update:DroneUpdate,route:List[Point]) -> DroneUpdateWithRoute:
    """creates a drone witha route o

    Args:
        drone_update: update
        route: rist of points

    Returns:
       DroneUpdateWithRoute: new object
    """
    if drone_update is None:
        return None

    if len(route) > 1:
        geojson = {'type': 'Feature',
                    'properties': {},
                    'geometry': mapping(LineString(route))}
    else:
        geojson = None

    return DroneUpdateWithRoute(
                    drone_id=drone_update.drone_id,
                    timestamp=drone_update.timestamp,
                    lon=drone_update.lon,
                    lat=drone_update.lat,
                    flight_range=drone_update.flight_range,
                    flight_time=drone_update.flight_time,
                    geojson=geojson)
