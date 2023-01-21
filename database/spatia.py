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

def spatiapoly_to_long_lat_arr(spatia_polygon:str)-> List[List[float]]:
    """converts an spatia POLYGON str into a long and lat floats tuple list.\n
    format: Polygon((1.2345 2.3456,1.2345 2.3456,1.2345 2.3456,1.2345 2.3456))

    Args:
        spatia_polygon (str): the spatia polygon as text.

    Returns:
        List[List[float]]: the cooridantes to the point as float value tuple list.
    """
    polygon = json.loads(spatia_polygon)
    return polygon['coordinates']

def coordinates_to_polygon(coordinates: List[List[float]], multi:bool =True) -> str:
    """generates the spatia polygon str.\n
    Polygon str format: 'POLYGON((x1 y1,x2 y2,..,xn yn))'

    Args:
        coordinates (List[List[float]]): coordinates of the polygon

    Returns:
        str: Spatia Polygon str.
    """
    # if len(coordinates) == 1:
    #     polygon_str = polygonhelper(coordinates[0])
    #     polygon_wkt = f'POLYGON({polygon_str})'
    # else:
    if not multi:
        coordinates = [coordinates]

    polygon_str=polygonhelper(coordinates[0])
    for index in range(1,len(coordinates)):
        poly_str = polygonhelper(coordinates[index])
        polygon_str += f',{poly_str}'

    polygon_wkt = f'MULTIPOLYGON({polygon_str})'

    return polygon_wkt

def polygonhelper(coordinates: List[List[float]]):
    #hier wird das polygon in seine bestandteile gesplittet
    poly_str = '('
    for layer in coordinates:
        first_coordinate = layer[0]
        polygon_wkt = f'({first_coordinate[0]} {first_coordinate[1]}'
        for index in range(1,len(layer)):
            polygon_wkt += f',{layer[index][0]} {layer[index][1]}'
        polygon_wkt +=')'
        if len(poly_str)>1:
            polygon_wkt = f',{polygon_wkt}'
        poly_str += polygon_wkt

    poly_str += ')'
    return poly_str
