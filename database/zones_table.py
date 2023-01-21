

import datetime
import json
import os
from typing import List
from api.dependencies.classes import DroneEvent, FireRisk, Zone
from database.database import create_table, fetched_match_class
from database.spatia import spatiapoly_to_long_lat_arr, coordinates_to_polygon
from database import drone_events_table
import database.database as db
import csv

CREATE_ZONE_TABLE = '''CREATE TABLE zones
(
id       integer NOT NULL ,
name    text NOT NULL ,
federal_state    text NOT NULL ,
district    text NOT NULL ,
PRIMARY KEY (id)
);

SELECT AddGeometryColumn('zones', 'area', 4326, 'MULTIPOLYGON', 'XY');'''
#   POLYGON((101.23 171.82, 201.32 101.5, 215.7 201.953, 101.23 171.82))
#   exterior ring, no interior rings
CREATE_ENTRY = 'INSERT INTO zones (name,federal_state,district,area) VALUES (?,?,?,GeomFromGeoJSON(?));'#GeomFromText(?,4326)
CREATE_ENTRY_TEXTGEO = 'INSERT INTO zones (name,federal_state,district,area) VALUES (?,?,?,GeomFromText(?,4326));'

GET_ZONE = '''SELECT id,name,federal_state,district,AsGeoJSON(area) AS area FROM zones
                JOIN ElementaryGeometries AS e ON (e.f_table_name = 'zones' 
                AND e.origin_rowid = zones.rowid)
                WHERE ST_Intersects(area, MakePoint(?, ?, 4326));'''

GET_ZONES = '''SELECT id,name,federal_state,district,AsGeoJSON(area) AS area FROM zones
                JOIN ElementaryGeometries AS e ON (e.f_table_name = 'zones' 
                AND e.origin_rowid = zones.rowid);'''

GET_ZONES_BY_DISTRICT = '''SELECT id,name,federal_state,district,AsGeoJSON(area) FROM zones WHERE district = ?'''

def setup():

    create_table(CREATE_ZONE_TABLE)
    path = os.path.realpath(os.path.dirname(__file__))
    with open(path+'/zonedata.json','r') as fin:
        data = json.load(fin)
# 'geo_point_2d':
# {'lon': 12.700551258771842, 'lat': 52.068172604501314}
# 'geo_shape':
# {'type': 'Feature', 'geometry': {'coordinates': [...], 'type': 'Polygon'}, 'properties': {}}
# 'year':'2021'
# 'lan_code':['12']
# 'lan_name':['Brandenburg']
# 'krs_code':['12069']
# 'krs_name':['Landkreis Potsdam-Mittelmark']
# 'vwg_code':['120695910']
# 'vwg_name':['Amt Niemegk']
# 'gem_code':['120695910448']
# 'gem_name':['Stadt Niemegk']
# 'gem_area_code':'DEU'
# 'gem_type':'Stadt'
# 'gem_name_short':['Niemegk']
        to_db = []
        for local_community in data:
            geo_json = local_community['geo_shape']
            
            new = {}
            #transform Polygons to Multipolygons
            new['type'] = 'MultiPolygon'
            if geo_json['geometry']['type'] == 'Polygon':
                new['coordinates'] = [geo_json['geometry']['coordinates']]
            else:
                new['coordinates'] = geo_json['geometry']['coordinates']
            
            #add SRID
            new['crs'] = {"type":"name","properties":{"name":"EPSG:4326"}}
            geo_json_str = json.dumps(new)
            #str = coordinates_to_polygon(new['coordinates'])
            insertuple = (  local_community['gem_name_short'][0],
                            local_community['lan_name'][0],
                            local_community['krs_name'][0],
                            geo_json_str)
            to_db.append(insertuple)

    inserted_id = db.insertmany(CREATE_ENTRY, to_db)
    print(inserted_id)


def create_zone(name,coordinates: List[List[float]])->bool:
    """stores geograhic area of a zone.
    Needs at least 3 coordinates to create a zone.

    Args:
        name (str): name of the zone.
        coordinates (List[tuple[float,float]]): A list containing at least 3 tuples with coordinates that mark the edge of the area.

    Returns:
        bool: Wether the zone could be created or not.
    """
    polygon_wkt = coordinates_to_polygon(coordinates)
    inserted_id = db.insert(CREATE_ENTRY_TEXTGEO,(name,polygon_wkt))
    if inserted_id:
        return True
    return False

def get_zone_of_coordinate(long,lat) -> Zone | None:
    """fetch the zone, the described point is in.

    Args:
        long (_type_): longitude of the point.
        lat (_type_): latitude of the point.

    Returns:
        Zone | None: the Zone if the point is inside a zones area, None if not.
    """
    fetched_zone = db.fetch_one(GET_ZONE,(long,lat))
    return get_obj_from_fetched(fetched_zone)

def get_zone_of_by_district(name:str) -> List[Zone] | None:
    """fetch the list of zones, in this district.

    Args:
        long (_type_): longitude of the point.
        lat (_type_): latitude of the point.

    Returns:
        Zone | None: the Zone if the point is inside a zones area, None if not.
    """
    fetched_zones = db.fetch_all(GET_ZONES_BY_DISTRICT,(name,))
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

def get_obj_from_fetched(   fetched_zone,
                            after:datetime.datetime=datetime.datetime.utcnow()-datetime.timedelta(days=1)
                        ) -> Zone | None:
    """generate Zone obj from fetched element.

    Args:
        fetched_zone (list): fetched attributes from zone.
        after (datetime): restriction to only select events that where created after this timestamp,
        defaults to 24h ago.

    Returns:
        Zone | None: zone object or None if obj cant be generated.
    """
    if fetched_match_class(Zone,fetched_zone,3):
        coord_array = spatiapoly_to_long_lat_arr(fetched_zone[4])
        
        events = drone_events_table.get_drone_events_in_zone(fetched_zone[4],after)

        if events:
            firerisk_enum = drone_events_table.calculate_firerisk(events)
        else:
            firerisk_enum = FireRisk(1)

        zone_obj = Zone(#TODO
            id = fetched_zone[0],
            name=fetched_zone[1],
            federal_state =fetched_zone[2],
            district=fetched_zone[3],
            coordinates=coord_array,
            events=events,
            fire_risk=firerisk_enum
        )
        return zone_obj
    return None
