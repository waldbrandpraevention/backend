import requests
import json
from shapely.geometry import shape, Point
import time

URL = "kiwa.tech/api/"
tickrate

#load drones
print d['glossary']['title']
drones_json = requests.get(URL + "simulation/get-drones/")
drones_dict = json.loads(drones_json)

last_execution = time.time()

while True:
    dt = time.time() - last_execution
    last_execution = time.time()
    for i in range(len(drones_dict)):
        drone = drones_dict[i]["drone"]
        geo_json = drones_dict[i]["geo_json"]
        vel = drones_dict[i]["direction"]
        speed = drones_dict[i]["speed"]
        new_x = drones_dict[i]["lat"] + vel[0] * speed * dt
        new_y = drones_dict[i]["long"] + vel[1] * speed * dt

        drones_dict[i]["lat"] = new_x
        drones_dict[i]["long"] = new_y

        point = Point(new_y new_x)

        found = False

        for feature in geo_json['features']:
            polygon = shape(feature['geometry'])
            if polygon.contains(point):
                found = True

        if not found:
            new_vel = (random(), random())

        #responses.post()