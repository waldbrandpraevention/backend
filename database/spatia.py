def spatiapoint_to_long_lat(spatia_point:str)-> tuple[float, float]:
    #POINT(1.2345 2.3456)
    float_vals = spatia_point.split('(')[1]
    float_vals = float_vals.replace(')','')
    #1.2345 2.3456
    coord_arr = float_vals.split(' ')
    long = float(coord_arr[0])
    lat = float(coord_arr[1])
    return long, lat
