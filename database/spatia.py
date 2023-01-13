from typing import List


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
    #Polygon((1.2345 2.3456,1.2345 2.3456,1.2345 2.3456,1.2345 2.3456))
    float_vals = spatia_polygon.split('(')[2]
    float_vals = float_vals.replace(')','')
    #1.2345 2.3456
    point_arr = float_vals.split(', ')
    polygon = []
    for coordinate in point_arr:
        coord_arr = coordinate.split(' ')
        long = float(coord_arr[0])
        lat = float(coord_arr[1])
        polygon.append([long,lat])
    return polygon

def coordinates_to_polygon(coordinates: List[List[float]]) -> str:
    """generates the spatia polygon str.\n
    Polygon str format: 'POLYGON((x1 y1,x2 y2,..,xn yn))'

    Args:
        coordinates (List[List[float]]): coordinates of the polygon

    Returns:
        str: Spatia Polygon str.
    """
    first_coordinate = coordinates[0]
    polygon_wkt = f'POLYGON(({first_coordinate[0]} {first_coordinate[1]}'
    for index in range(1,len(coordinates)):
        polygon_wkt += f',{coordinates[index][0]} {coordinates[index][1]}'
    polygon_wkt +='))'

    return polygon_wkt
