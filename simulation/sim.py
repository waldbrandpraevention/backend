"""functions for the simulation"""
import requests
import json
import time
from shapely.geometry import shape, Point
import time
import os, random
from datetime import datetime, timedelta
from .cv import ai_prediction, Result
from io import StringIO 

from api.dependencies.classes import DroneUpdate, DroneEvent, EventType


ASSETS = "./simulation/assets/raw/"
URL = "kiwa.tech/api/"
CHANCE_OF_EVENT = 0.001

time.sleep(1)

#load drones
drones_dict = None
try:
    drones_json = requests.get(URL + "simulation/all-drones/")
    text = response.text
    drones_dict = json.loads(text)

except Exception as e:
    print("error:")
    print(e)
    drondrones_dict = {}

last_execution = datetime.now()
next_update = datetime.now()
delta = timedelta(minutes=10)


def simulate():
    try:
        while True:
            dt = datetime.now() - last_execution
            last_execution = datetime.now()
            for i in range(len(drones_dict)):
                drone = drones_dict[i]["drone"]
                geo_json = drones_dict[i]["geo_json"]
                vel = drones_dict[i]["direction"]
                speed = drones_dict[i]["speed"]
                new_x = drones_dict[i]["lat"] + vel[0] * speed * dt
                new_y = drones_dict[i]["lon"] + vel[1] * speed * dt

                point = Point(new_y, new_x)

                found = False

                for feature in geo_json['features']:
                    polygon = shape(feature['geometry'])
                    if polygon.contains(point):
                        found = True

                if not found: #not in polygon just turn randomly
                    new_angle = random.uniform(0, 6.28318530718)
                    x = 1 * cos(new_angle)
                    y = 1 * sin(new_angle)

                    drones_dict[i]["direction"] = (x, y)
                else:
                    drones_dict[i]["lat"] = new_x
                    drones_dict[i]["lon"] = new_y

                if datetime.now() >= next_update:
                    next_update = datetime.now() + delta

                    distance = math.hypot(drones_dict[i]["last_update"]["lon"] - drones_dict[i]["lon"],
                            drones_dict[i]["last_update"]["lat"] - drones_dict[i]["lat"])
                    new_update = DroneUpdate(
                        drone_id = drones_dict[i]["drone"]["id"],
                        timestamp = datetime.now(),
                        longitude = drones_dict[i]["lon"],
                        latitude = drones_dict[i]["lat"],
                        flight_range = drones_dict[i]["drone"]["flight_range"] + distance,
                        flight_time = drones_dict[i]["drone"]["flight_time"] + time_differenze
                        )

                    payload = {'update': new_update}
                    responses.post(URL + "drones/send-update/", params=payload)   

                    if random() <= CHANCE_OF_EVENT: #event happens as well
                        #pick random file
                        file_name = random.choice(os.listdir(ASSETS))
                        path = os.path.join(ASSETS, filename)

                    results = ai_prediction(path)

                    for r in results:
                        event = DroneEvent(
                        drone_id = drones_dict[i]["drone"]["id"],
                        timestamp = datetime.now(),
                        longitude = drones_dict[i]["lon"],
                        latitude = drones_dict[i]["lat"],
                        event_type = r.event_type,
                        confidence = r.confidence,
                        csv_file_path = None,
                        )
                        payload = {'event': event}
                        #might be needed
                        img_io = StringIO()
                        r.picture.save(img_io, 'JPEG', quality=70)
                        img_io.seek(0)
                        files = {'file:': img_io}
                        #files = {'file:': r.picture}
                        responses.post(URL + "drones/send-event/", params=payload, files=files) 
    except Exception as e:
        print("Simulation failed:")
        print(e)