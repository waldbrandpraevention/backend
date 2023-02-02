import requests
import json
from shapely.geometry import shape, Point
import time
import os, random
from datetime import datetime

from api.dependencies.classes import DroneUpdate, DroneEvent, EventType

ASSETS = "./assets/"
URL = "kiwa.tech/api/"
CHANCE_OF_EVENT = 0.5

#load drones
drones_json = requests.get(URL + "simulation/get-drones/")
drones_dict = json.loads(drones_json)

last_execution = time.time()

last_update = time.time()

def evaluate_image(path):
    return EventType.FIRE




while True:
    dt = time.time() - last_execution
    last_execution = time.time()
    for i in range(len(drones_dict)):
        drone = drones_dict[i]["drone"]
        geo_json = drones_dict[i]["geo_json"]
        vel = drones_dict[i]["direction"]
        speed = drones_dict[i]["speed"]
        new_x = drones_dict[i]["lat"] + vel[0] * speed * dt
        new_y = drones_dict[i]["lon"] + vel[1] * speed * dt

        drones_dict[i]["lat"] = new_x
        drones_dict[i]["lon"] = new_y

        point = Point(new_y new_x)

        found = False

        for feature in geo_json['features']:
            polygon = shape(feature['geometry'])
            if polygon.contains(point):
                found = True

        if not found: #not in polygon
            new_angle = random.uniform(0, 6.28318530718)
            x = 1 * cos(new_angle)
            y = 1 * sin(new_angle)

            new_vel = (x, y)

        time_differenze = time.time() - last_update
        if time_differenze > 10:
            distance = math.hypot(drones_dict[i]["last_update"]["lon"] - drones_dict[i]["lon"],
                    drones_dict[i]["last_update"]["lat"] - drones_dict[i]["lat"])
            new_update = DroneUpdate(
                drone_id = drones_dict[i]["drone"]["id"],
                timestamp = datetime.now(),
                longitude = drones_dict[i]["lon"],
                latitude = drones_dict[i]["lat"],
                flight_range: drones_dict[i]["drone"]["flight_range"] + distance
                flight_time: drones_dict[i]["drone"]["flight_time"] + time_differenze
                )

            if random() <= CHANCE_OF_EVENT: #event happens as well
                #pick random file
                file_name = random.choice(os.listdir(ASSETS))
                path = os.path.join(ASSETS, filename)

            DroneEvent(
                drone_id = drones_dict[i]["drone"]["id"],
                timestamp datetime.now(),
                longitude = drones_dict[i]["lon"],
                latitude = drones_dict[i]["lat"],
                event_type = evaluate_image(path)
                confidence: int | None = None
                picture_path = path
                ai_predictions :dict| None = None
                csv_file_path :str| None = None
                )




        #responses.post(URL + drones/......) #todo