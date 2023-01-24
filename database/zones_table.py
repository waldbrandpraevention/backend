"This module contains functions to create and fetch zones, stored in the db"
import datetime
import json
from typing import List
from api.dependencies.classes import FireRisk, Zone
from database.database import fetched_match_class
from database.spatia import coordinates_to_multipolygonstr, spatiageostr_to_geojson
from database import drone_events_table
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
SELECT AddGeometryColumn('zones', 'area', 4326, 'MULTIPOLYGON', 'XY');'''
#   POLYGON((101.23 171.82, 201.32 101.5, 215.7 201.953, 101.23 171.82))
#   exterior ring, no interior rings
CREATE_ENTRY = '''INSERT INTO zones (name,federal_state,district,area) 
                VALUES (?,?,?,GeomFromGeoJSON(?));'''
CREATE_ENTRY_TEXTGEO = '''INSERT OR IGNORE INTO zones (id, name,federal_state,district,area) 
                        VALUES (?,?,?,?,GeomFromText(?,4326));'''

GET_ZONE = '''SELECT id,name,federal_state,district,AsGeoJSON(area) AS area FROM zones
                JOIN ElementaryGeometries AS e ON (e.f_table_name = 'zones' 
                AND e.origin_rowid = zones.rowid)
                WHERE ST_Intersects(area, MakePoint(?, ?, 4326));'''

GET_ZONES = '''SELECT id,name,federal_state,district,AsGeoJSON(area) AS area FROM zones
                JOIN ElementaryGeometries AS e ON (e.f_table_name = 'zones' 
                AND e.origin_rowid = zones.rowid);'''

GET_ZONES_BY_DISTRICT = '''SELECT id,name,federal_state,district,AsGeoJSON(area) 
                            FROM zones 
                            WHERE district = ?'''


def load_from_geojson(path_to_geojson) -> int:
    """load data from a geojson file to the db.
    required fields:
    'features':{
        [
            'geometry': {'coordinates': [...], 'type': 'Polygon'},
            'properties':{
                'lan_name':['Bundesland']
                'krs_name':['Landkreis Name']
                'gem_name_short':['Name']
                'gem_code':['100440114114']
        ],
    }

    Args:
        path_to_geojson (_type_): path to the geojson that should be imported.

    Returns:
        int: number of inserted zones.
    """
    with open(path_to_geojson, 'r') as geof:
        data = json.load(geof)
        to_db = []
        for local_community in data['features']:
            text = coordinates_to_multipolygonstr(local_community['geometry'])
            insertuple = (local_community['properties']['gem_code'][0],
                          local_community['properties']['gem_name_short'][0],
                          local_community['properties']['lan_name'][0],
                          local_community['properties']['krs_name'][0],
                          text)
            to_db.append(insertuple)

    rowcount = db.insertmany(CREATE_ENTRY_TEXTGEO, to_db)
    
    return rowcount


def create_zone(gem_code, name, federal_state, district, gemometry: dict) -> bool:
    """stores geograhic area of a zone.
    Needs at least 3 coordinates to create a zone.

    Args:
        name (str): name of the zone.
        geometry (dict): dict which contains the coordinates and the type. Working with SRID 4326.
        "geometry": {
            "type": "Polygon",
            "coordinates": [[[8.127194650631184, 48.75522682270608], more coordinates], interior rings...]
        }
        "geometry": {
            "type": "MultiPolygon",
            "coordinates": [[[[8.127194650631184, 48.75522682270608], more coordinates], interior rings...], more Polygons]
        }

    Returns:
        bool: Wether the zone could be created or not.
    """
    polygon_wkt = coordinates_to_multipolygonstr(gemometry)
    inserted_id = db.insert(
        CREATE_ENTRY_TEXTGEO, (gem_code, name, federal_state, district, polygon_wkt))
    if inserted_id:
        return True
    return False


def get_zone_of_coordinate(long, lat) -> Zone | None:
    """fetch the zone, the described point is in.

    Args:
        long (_type_): longitude of the point.
        lat (_type_): latitude of the point.

    Returns:
        Zone | None: the Zone if the point is inside a zones area, None if not.
    """
    fetched_zone = db.fetch_one(GET_ZONE, (long, lat))
    return get_obj_from_fetched(fetched_zone)


def get_zone_of_by_district(name: str) -> List[Zone] | None:
    """fetch the list of zones, in this district.

    Args:
        long (_type_): longitude of the point.
        lat (_type_): latitude of the point.

    Returns:
        Zone | None: the Zone if the point is inside a zones area, None if not.
    """
    fetched_zones = db.fetch_all(GET_ZONES_BY_DISTRICT, (name,))
    if fetched_zones:
        output = []
        for zone in fetched_zones:
            zone_obj = get_obj_from_fetched(zone)
            if zone_obj:
                output.append(zone_obj)
        return output
    return None


def get_zones() -> List[Zone]:
    """get a list of all zones.

    Returns:
        List[Zone]: list containing Zone obj.
    """
    fetched_zones = db.fetch_all(GET_ZONES)
    if fetched_zones:
        output = []
        for zone in fetched_zones:
            zone_obj = get_obj_from_fetched(zone)
            if zone_obj:
                output.append(zone_obj)
        return output
    return None


def get_obj_from_fetched(
                fetched_zone,
                after: datetime.datetime = datetime.datetime.utcnow()-datetime.timedelta(days=1)
                ) -> Zone | None:
    """generate Zone obj from fetched element.

    Args:
        fetched_zone (list): fetched attributes from zone.
        after (datetime): restriction to only select events that where created after this timestamp,
        defaults to 24h ago.

    Returns:
        Zone | None: zone object or None if obj cant be generated.
    """
    if fetched_match_class(Zone, fetched_zone, 3):
        geo_json = spatiageostr_to_geojson(fetched_zone[4])

        events = drone_events_table.get_drone_events_in_zone(
            fetched_zone[4], after)

        if events:
            firerisk_enum = drone_events_table.calculate_firerisk(events)
        else:
            firerisk_enum = FireRisk(1)

        zone_obj = Zone(  #TODO
            id=fetched_zone[0],
            name=fetched_zone[1],
            federal_state=fetched_zone[2],
            district=fetched_zone[3],
            geo_json=geo_json,
            events=events,
            fire_risk=firerisk_enum
        )
        return zone_obj
    return None
