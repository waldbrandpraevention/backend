"""Module for sparta lite"""
import json
from typing import List

geo_types = {'Point', 'MultiPoint', 'LineString', 'MultiLineString',
             'Polygon', 'MultiPolygon'}

wkt_types = {x.upper() for x in geo_types}

type_translations = {x.upper(): x for x in geo_types}

def spatiapoint_to_long_lat(spatia_point:str)-> tuple[float, float]:
    """converts an spatia POINT str into long and lat floats tuple.\n
    format: POINT(1.2345 2.3456)

    Args:
        spatia_point (str): the spatia point as text.

    Returns:
        tuple[float, float]: the cooridantes to the point as float value tuple.
    """
    #POINT(1.2345 2.3456)
    float_vals = spatia_point.split('(')[1]
    float_vals = float_vals.replace(')','')
    #1.2345 2.3456
    coord_arr = float_vals.split(' ')
    long = float(coord_arr[0])
    lat = float(coord_arr[1])
    return long, lat


def spatiageostr_to_geojson(spatia_polygon:str,properties:dict=None)-> dict:
    """converts an spatia geojson str into a geodict.\n

    Args:
        spatia_polygon (str): the geodict geometry as text.

    Returns:
        dict: the geojson.
    """
    geometry = json.loads(spatia_polygon)
    geo_json = {
                "type": "Feature",
                "geometry": geometry
                }
    if properties is not None:
        geo_json['properties'] = properties

    return geo_json

def coordinates_to_multipolygonstr(geometry: dict) -> str:
    """generates the spatia polygon str.\n
    MultiPolygon str format: 'MULTIPOLYGON(((x1 y1,x2 y2,..,xn yn)))'

    Args:
        geometry (dict): dict which contains the coordinates and the type. Working with SRID 4326.
        "geometry": {
            "type": "Polygon",
            "coordinates": [[[8.127194650631184, 48.75522682270608], more coordinates],
                 interior rings...]
        }
        "geometry": {
            "type": "MultiPolygon",
            "coordinates": [[[[8.127194650631184, 48.75522682270608], more coordinates],
                                 interior rings...],  more Polygons]
        }

    Returns:
        str: Spatia MultiPolygon str.
    """
    if not (geometry['type'] == 'Polygon' or geometry['type'] == 'MultiPolygon'):
        return None

    coordinates = geometry['coordinates']
    if  geometry['type'] == 'Polygon':
        coordinates = [coordinates]

    polygon_iter = iter(coordinates)
    first_polygon = next(polygon_iter)
    polygon_str = polygonhelper(first_polygon)
    for polygon in polygon_iter:
        poly_str = polygonhelper(polygon)
        polygon_str += f',{poly_str}'

    polygon_wkt = f'MULTIPOLYGON({polygon_str})'

    return polygon_wkt

def polygonhelper(coordinates: List[List[List[float]]]):
    """this function gets single Polygons and generates the coresponding Spatia str.
    Polygon str format: 'POLYGON((x1 y1,x2 y2,..,xn yn))'

    Args:
        coordinates (List[List[List[float]]]): Array containing the coordinates of the Polygon.

    Returns:
        str: Spatia Polygon str.
    """
    #hier wird das polygon in seine bestandteile gesplittet
    poly_str = '('
    ring_iter = iter(coordinates)
    first_polygon_ring = next(ring_iter)
    poly_str += polygon_coordinates_helper(first_polygon_ring)
    for polygon_ring in ring_iter:
        polygon_wkt = polygon_coordinates_helper(polygon_ring)
        poly_str += f',{polygon_wkt}'

    poly_str += ')'
    return poly_str

def polygon_coordinates_helper(coordinates: List[List[float]]):
    """this function gets coordinates and generates the coresponding Spatia str.
    Coordinate str format: '(x1 y1,x2 y2,..,xn yn)'

    Args:
        coordinates (List[List[float]]): Array containing coordinates.

    Returns:
        str: Spatia Coordinates str.
    """
    polygon_wkt = '('
    cord_iter = iter(coordinates)
    first_long_lat = next(cord_iter)
    polygon_wkt += f'{first_long_lat[0]} {first_long_lat[1]}'

    for long_lat in cord_iter:
        polygon_wkt += f',{long_lat[0]} {long_lat[1]}'

    polygon_wkt +=')'

    return polygon_wkt

def geojson_insert_text(geometry):
    """Inserts text into a geojson

    Args:
        geometry (_type_): goemotry object

    Returns:
        json: geojson
    """
    geo_json = {}
    geo_json = {'type':'MultiPolygon'}

    #transform Polygons to Multipolygons
    if geometry['type'] == 'Polygon':
        geo_json['coordinates'] = [geometry['coordinates']]
    else:
        geo_json['coordinates'] = geometry['coordinates']

    geo_json['crs'] = {"type":"name","properties":{"name":"EPSG:4326"}}
    return json.dumps(geo_json)
