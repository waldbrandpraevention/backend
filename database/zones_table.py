"""This module contains functions to create and fetch zones, stored in the db.
we used https://data.opendatasoft.com/explore/dataset/georef-germany-gemeinde%40public/table for the zone_data geoJSON"""
import datetime
from enum import Enum
import json
from typing import List
from api.dependencies.classes import FireRisk, Zone
from database.database import add_where_clause, create_where_clause_statement, fetched_match_class
from database.spatia import coordinates_to_multipolygonstr, spatiageostr_to_geojson
from database import drone_events_table, drone_updates_table
import database.database as db

CREATE_ZONE_TABLE = '''CREATE TABLE zones
(
id       integer NOT NULL ,
name    text NOT NULL ,
federal_state    text NOT NULL ,
district    text NOT NULL ,
PRIMARY KEY (id)
);
CREATE INDEX IF NOT EXISTS zones_AK ON zones (name);
SELECT AddGeometryColumn('zones', 'area', 4326, 'MULTIPOLYGON', 'XY');
SELECT AddGeometryColumn('zones', 'geo_point', 4326, 'POINT', 'XY');'''
#   POLYGON((101.23 171.82, 201.32 101.5, 215.7 201.953, 101.23 171.82))
#   exterior ring, no interior rings

class ZoneWhereClause(str, Enum):
    """Class for zones with a where clause"""
    MAKEPOINTINTERSECT = 'ST_Intersects(zones.area, MakePoint(?, ?, 4326))'
    GEOJSONINTERSECT = 'ST_Intersects(zones.area, GeomFromGeoJSON(?))'
    ZONE_ID = 'zones.id'

CREATE_ENTRY = '''INSERT INTO zones (name,federal_state,district,area,geo_point)
                VALUES (?,?,?,GeomFromGeoJSON(?),MakePoint(?, ?, 4326));'''

CREATE_ENTRY_TEXTGEO = '''INSERT OR IGNORE
                        INTO zones (id, name,federal_state,district,area,geo_point) 
                        VALUES (?,?,?,?,GeomFromText(?,4326),MakePoint(?, ?, 4326));'''

GET_ZONE = """SELECT zones.id,zones.name,federal_state,district,AsGeoJSON(area),
                X(geo_point),Y(geo_point),
                Count(DISTINCT newdrone_data.drone_id),
                newdrone_data.ts,
                Count(DISTINCT drone_event.id)
                FROM zones
                LEFT OUTER JOIN drone_event ON ST_Intersects(drone_event.coordinates, area)
                LEFT OUTER JOIN ( 
                            SELECT coordinates, MAX(timestamp) as ts, drone_id
                            from drone_data
                            group by drone_data.drone_id
                    ) AS newdrone_data
                ON ST_Intersects(newdrone_data.coordinates, area)
                {}
                GROUP BY name
                ORDER BY name;"""

GET_ZONEPOLYGON = """   SELECT AsGeoJSON(area)
                        FROM zones
                        {}"""

GET_ZONEJOINORGA ='''SELECT zones.id,zones.name,federal_state,district,AsGeoJSON(area),
                        X(geo_point),Y(geo_point),
                        Count(DISTINCT newdrone_data.drone_id),
                    newdrone_data.ts,
                    Count(DISTINCT drone_event.id)
                    FROM zones
                    JOIN territory_zones 
                    ON zones.id = territory_zones.zone_id
                    JOIN territories ON territories.id = territory_zones.territory_id
                    LEFT OUTER JOIN drone_event ON ST_Intersects(drone_event.coordinates, area)
                    LEFT OUTER JOIN (  
                            SELECT coordinates, MAX(timestamp) as ts, drone_id
                            from drone_data
                            group by drone_data.drone_id
                    ) AS newdrone_data
                    ON ST_Intersects(newdrone_data.coordinates, area)

                    WHERE zones.{}=? 
                    AND territories.orga_id=?
                    GROUP BY zones.name
                    ORDER BY zones.name;'''

GET_ZONES_BY_DISTRICT = '''SELECT zones.id,zones.name,federal_state,district,AsGeoJSON(area),
                            X(geo_point),Y(geo_point),Count(DISTINCT newdrone_data.drone_id),
                            newdrone_data.ts,
                            Count(DISTINCT drone_event.id)
                            FROM zones
                            LEFT OUTER JOIN drone_event ON ST_Intersects(drone_event.coordinates, area)
                            LEFT OUTER JOIN ( 
                                    SELECT coordinates, MAX(timestamp) as ts, drone_id
                                    from drone_data
                                    group by drone_data.drone_id
                            ) AS newdrone_data
                            ON ST_Intersects(newdrone_data.coordinates, area)
                            WHERE district = ?
                            GROUP BY zones.name;'''

GET_ORGAZONES = '''  SELECT zones.id,zones.name,federal_state,district,AsGeoJSON(area),
                    X(geo_point),
                    Y(geo_point),
                    Count(DISTINCT newdrone_data.drone_id),
                    newdrone_data.ts,
                    Count(DISTINCT drone_event.id)
                    FROM zones
                    JOIN territory_zones 
                    ON zones.id = territory_zones.zone_id
                    JOIN territories ON territories.id = territory_zones.territory_id
                    LEFT OUTER JOIN drone_event ON ST_Intersects(drone_event.coordinates, area)
                    LEFT OUTER JOIN ( 
                                    SELECT coordinates, MAX(timestamp) as ts, drone_id
                                    from drone_data
                                    group by drone_data.drone_id
                            ) AS newdrone_data
                    ON ST_Intersects(newdrone_data.coordinates, area)
                    WHERE territories.orga_id=?
                    GROUP BY zones.name;'''


def add_from_geojson(path_to_geojson) -> int:
    """add zone data from a geojson file to the db.
    https://data.opendatasoft.com/explore/dataset/georef-germany-gemeinde%40public/table
    required fields:
    'features':[
        {
            'geometry': {'coordinates': [...], 'type': 'Polygon'},
            'properties':{
                'lan_name':['Bundesland']
                'krs_name':['Landkreis Name']
                'gem_name_short':['Name']
                'gem_code':['100440114114']
                'geo_point_2d':{
                    'lon':12.947508749154961,
                    'lat':52.22729704994886
                }
            }
        },...
    ]

    Args:
        path_to_geojson (str): path to the geojson that should be imported.

    Returns:
        int: number of inserted zones.
    """
    with open(path_to_geojson, 'r',encoding="utf-8") as geof:
        data = json.load(geof)
        to_db = []
        for local_community in data['features']:
            text = coordinates_to_multipolygonstr(local_community['geometry'])
            insertuple = (local_community['properties']['gem_code'][0],
                          local_community['properties']['gem_name_short'][0],
                          local_community['properties']['lan_name'][0],
                          local_community['properties']['krs_name'][0],
                          text,
                          local_community['properties']['geo_point_2d']['lon'],
                          local_community['properties']['geo_point_2d']['lat'])
            to_db.append(insertuple)

    rowcount = db.insertmany(CREATE_ENTRY_TEXTGEO, to_db)

    return rowcount


def create_zone(gem_code, name, federal_state, district, gemometry: dict, geo_point: tuple) -> bool:
    """stores geograhic area of a zone.
    Needs at least 3 coordinates to create a zone.

    Args:
        name (str): name of the zone.
        geometry (dict): dict which contains the coordinates and the type. Working with SRID 4326.
        "geometry": {
            "type": "Polygon",
            "coordinates": [[[8.127194650631184, 48.75522682270608], more coordinates],
                                 interior rings...]
        }
        "geometry": {
            "type": "MultiPolygon",
            "coordinates": [[[[8.127194650631184, 48.75522682270608], more coordinates],
                             interior rings...], more Polygons]
        }

    Returns:
        bool: Wether the zone could be created or not.
    """
    polygon_wkt = coordinates_to_multipolygonstr(gemometry)
    inserted_id = db.insert(
        CREATE_ENTRY_TEXTGEO,
            (
            gem_code,
            name,
            federal_state,
            district,
            polygon_wkt,
            geo_point[0],
            geo_point[1]
            )
        )
    if inserted_id:
        return True
    return False

def get_zone(zone_id:int) -> Zone | None:
    """fetch the zone.

    Args:
        zone_id (int): id of the zone.

    Returns:
        Zone | None: the Zone.
    """
    where_arr = create_where_clause_statement(ZoneWhereClause.ZONE_ID,'=')
    sql = add_where_clause(GET_ZONE,[where_arr])
    fetched_zone = db.fetch_one(sql, (zone_id,))
    return get_obj_from_fetched(fetched_zone)

def get_zone_polygon(zone_id:int) -> str:
    """get the polygon of a zone.

    Args:
        zone_id (int): id of the zone.

    Returns:
        str: the polygon of the zone as geo_json str.

    """
    stm = create_where_clause_statement(ZoneWhereClause.ZONE_ID,'=')
    sql = add_where_clause(GET_ZONEPOLYGON,[stm])
    fetched_polygon = db.fetch_one(sql, (zone_id,))
    if fetched_polygon is not None:
        return fetched_polygon[0]
    return None


def get_zone_of_coordinate(long:float, lat:float) -> Zone | None:
    """fetch the zone, the given lat lon tuple is in.

    Args:
        long (float): longitude of the point.
        lat (float): latitude of the point.

    Returns:
        Zone | None: the Zone if the point is inside a zones area, None if not.
    """
    sql = add_where_clause(GET_ZONE,[ZoneWhereClause.MAKEPOINTINTERSECT])
    fetched_zone = db.fetch_one(sql, (long, lat))
    return get_obj_from_fetched(fetched_zone)

def get_zones_in_area(area:str) -> List[Zone] | None:
    """fetch all zones in the given area.

    Args:
        area (str): geojson string of the area.

    Returns:
        List[Zone] | None: list of zones in the area.
    """
    sql = add_where_clause(GET_ZONE,[ZoneWhereClause.GEOJSONINTERSECT])
    fetched_zones = db.fetch_all(sql, (area,))

    if fetched_zones is None:
        return None

    output = []
    for zone in fetched_zones:
        zone_obj = get_obj_from_fetched(zone)
        if zone_obj:
            output.append(zone_obj)
    return output


def get_zone_of_district(name: str) -> List[Zone] | None:
    """list all zones of this district.

    Args:
        name (str): name of the district.

    Returns:
        List[Zone] | None: list of zones in the district.
    """
    fetched_zones = db.fetch_all(GET_ZONES_BY_DISTRICT, (name,))
    if fetched_zones is None:
        return None

    output = []
    for zone in fetched_zones:
        zone_obj = get_obj_from_fetched(zone)
        if zone_obj:
            output.append(zone_obj)
    return output


def get_zones() -> List[Zone]:
    """get a list of all zones.

    Returns:
        List[Zone]: list containing Zone obj.
    """
    sql = GET_ZONE.format('')
    fetched_zones = db.fetch_all(sql)
    if fetched_zones is None:
        return None
    output = []
    for zone in fetched_zones:
        zone_obj = get_obj_from_fetched(zone)
        if zone_obj:
            output.append(zone_obj)
    return output

def get_active_drone_count(polygon: str,
                           after: datetime.datetime = None) -> int:
    """counts the number of actives drones in a area.

    Args:
        polygon (str): _description_
        after (datetime.datetime, optional): _description_. Defaults to None.

    Returns:
        int: _description_
    """
    drones = drone_updates_table.get_active_drones(polygon,after)

    if drones is None:
        return 0

    return len(drones)

def get_obj_from_fetched(
                fetched_zone,
                after: datetime.datetime = datetime.datetime.utcnow()-datetime.timedelta(days=3)
                ) -> Zone | None:
    """generate Zone obj from fetched element.

    Args:
        fetched_zone (list): fetched attributes from the zone.
        after (datetime): restriction to only select events that where created after this timestamp,
        defaults to 24h ago.

    Returns:
        Zone | None: zone object or None if obj cant be generated.
    """
    if fetched_match_class(Zone, fetched_zone,4):
        geo_json = spatiageostr_to_geojson(fetched_zone[4])

        try:
            if fetched_zone[9] > 0:
                events = drone_events_table.get_drone_event(
                                            polygon=fetched_zone[4],
                                            after=after)
            else:
                events = None
        except IndexError:
            events = None
            print('no events found')

        try:
            la_timestam = fetched_zone[8]
        except IndexError:
            la_timestam = None

        if events:
            ai_firerisk_enum, firerisk, smokerisk = drone_events_table.calculate_firerisk(events)
        else:
            ai_firerisk_enum= FireRisk(0)
            firerisk= FireRisk(0)
            smokerisk  = FireRisk(0)

        try:
            lon = fetched_zone[5]
            lat= fetched_zone[6]
        except IndexError:
            lon = None
            lat= None

        zone_obj = Zone(
            id=fetched_zone[0],
            name=fetched_zone[1],
            federal_state=fetched_zone[2],
            district=fetched_zone[3],
            geo_json=geo_json,
            events=events,
            ai_fire_risk=ai_firerisk_enum,
            lon=lon,
            lat=lat,
            last_update=la_timestam,
            drone_count=fetched_zone[7],
            ai_fire_detection=firerisk,
            ai_smoke_detection=smokerisk
        )
        return zone_obj
    return None
