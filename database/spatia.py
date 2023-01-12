from typing import List


def spatiapoint_to_long_lat(spatia_point:str)-> tuple[float, float]:
    #POINT(1.2345 2.3456)
    float_vals = spatia_point.split('(')[1]
    float_vals = float_vals.replace(')','')
    #1.2345 2.3456
    coord_arr = float_vals.split(' ')
    long = float(coord_arr[0])
    lat = float(coord_arr[1])
    return long, lat

def spatiapoly_to_long_lat_arr(spatia_point:str)-> List[List[float]]:
    #Polygon((1.2345 2.3456,1.2345 2.3456,1.2345 2.3456,1.2345 2.3456))
    float_vals = spatia_point.split('(')[2]
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
