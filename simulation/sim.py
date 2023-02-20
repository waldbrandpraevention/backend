"""functions for the simulation"""
import json
import time
import os
import random
import math
from io import StringIO
from datetime import datetime, timedelta
import requests
from shapely.geometry import shape, Point
from api.dependencies.classes import DroneUpdate, DroneEvent
from .cv import ai_prediction

ASSETS = "./simulation/assets/raw/"
URL = os.getenv("DOMAIN_API")
admin_mail = os.getenv("ADMIN_MAIL")
admin_password = os.getenv("ADMIN_PASSWORD")
CHANCE_OF_EVENT = 0.001

def login():
    login_data = {"username": admin_mail, "password": admin_password}
    login_response = requests.post(URL+"/users/login/", data=login_data)
    login_json_response = login_response.json()
    token = login_json_response["access_token"]
    return token


def setup():
    token = login()
    header = {"Authorization:" "Bearer " + token}
    response = requests.post(URL+"/territories/all/", headers=header, timeout=10)
    signup_json_response = response.json()


def create_new_drone():
    """creates a new drone

    Returns:
        token + drone
    """
    token = login()

    drone = {
        "name": f"Drone-{random.randint(1, 100000)}",
        "drone_type": "Unmanned Aerial Vehicle",
        "cc_range": random.randrange(5.0, 100.0),
        "flight_range": random.randrange(50.0, 500.0),
        "flight_time": random.randrange(50.0, 150.0)
    }

    header = {"Authorization:" "Bearer " + token}
    response = requests.post(URL+"/drones/signup/", headers=header, params=drone, timeout=10)
    signup_json_response = response.json()

    angle = random.random()
    simulation_drone = {
        "drone": signup_json_response["drone"],
        "token": signup_json_response["token"],
        "geo_json": "",
        "speed": random.randrange(0.00001, 0.000001),
        "direction": (math.cos(angle), math.sin(angle)),
        "lat": zones[rand].lat,
        "lon": zones[rand].lan
    }
    return json_response


def simulate():
    """simulates drones in a loop
    """
    drones = []
    while len(drones) < 5:
        try:
            drones.append(create_new_drone())
        except Exception as err:
            print("Simulation Error: Unable to create drone. Retrying in 5sec")
            print(err)
            time.sleep(5)


    last_execution = datetime.now()
    next_update = datetime.now()
    delta = timedelta(minutes=10)
    while True:
        try:
            delta_time = datetime.now() - last_execution
            last_execution = datetime.now()

            for drone_entry in drones:
                geo_json = drone_entry["geo_json"]
                vel = drone_entry["direction"]
                speed = drone_entry["speed"]
                new_x = drone_entry["lat"] + vel[0] * speed * delta_time
                new_y = drone_entry["lon"] + vel[1] * speed * delta_time

                point = Point(new_y, new_x)

                found = False

                for feature in geo_json['features']:
                    polygon = shape(feature['geometry'])
                    if polygon.contains(point):
                        found = True

                if not found: #not in polygon just turn randomly
                    new_angle = random.uniform(0, 6.28318530718)
                    dir_x = 1 * math.cos(new_angle)
                    dir_y = 1 * math.sin(new_angle)

                    drone_entry["direction"] = (dir_x, dir_y)
                else:
                    drone_entry["lat"] = new_x
                    drone_entry["lon"] = new_y

                if datetime.now() >= next_update:
                    next_update = datetime.now() + delta

                    distance = math.hypot(drone_entry["last_update"]["lon"] - drone_entry["lon"],
                            drone_entry["last_update"]["lat"] - drone_entry["lat"])
                    new_update = DroneUpdate(
                        drone_id = drone_entry["drone"]["id"],
                        timestamp = datetime.now(),
                        longitude = drone_entry["lon"],
                        latitude = drone_entry["lat"],
                        flight_range = drone_entry["drone"]["flight_range"] + distance,
                        flight_time = drone_entry["drone"]["flight_time"] + 10
                        )

                    payload = {'update': new_update}
                    requests.post(URL + "drones/send-update/", params=payload)

                    if random.random() <= CHANCE_OF_EVENT: #event happens as well
                        #pick random file
                        file_name = random.choice(os.listdir(ASSETS))
                        path = os.path.join(ASSETS, file_name)

                    results = ai_prediction(path)
                    for result in results:
                        event = DroneEvent(
                        drone_id = drone_entry["drone"]["id"],
                        timestamp = datetime.now(),
                        longitude = drone_entry["lon"],
                        latitude = drone_entry["lat"],
                        event_type = result.event_type,
                        confidence = result.confidence,
                        csv_file_path = None,
                        )
                        payload = {'event': event}
                        #might be needed
                        img_io = StringIO()
                        result.picture.save(img_io, 'JPEG', quality=70)
                        img_io.seek(0)
                        files = {'file:': img_io}
                        #files = {'file:': r.picture}
                        requests.post(URL + "drones/send-event/", params=payload, files=files)
        except Exception as err2:
            print("Simulation error:\n")
            print(err2)
