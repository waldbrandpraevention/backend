"""functions for the simulation"""
import json
import time
import os
import random
import math
from io import BytesIO
from datetime import datetime, timedelta
import requests
from shapely.geometry import shape, Point
from fastapi import HTTPException
from api.dependencies.classes import DroneUpdate, DroneEvent
from api.dependencies.territories import get_territories
from database.drone_updates_table import create_drone_update
from .cv import ai_prediction
from database import territories_table

ASSETS = "./simulation/assets/raw/"
URL = os.getenv("DOMAIN_API")
admin_mail = os.getenv("ADMIN_MAIL")
admin_password = os.getenv("ADMIN_PASSWORD")
CHANCE_OF_EVENT = 0.001

#todo

def login():
    """login for the simulation"""
    login_data = {"username": admin_mail, "password": admin_password}
    login_response = requests.post(URL+"/users/login/", data=login_data, timeout=10)
    login_json_response = login_response.json()
    token = login_json_response["access_token"]
    return token

def get_territories_from_user(token):
    """gets the territories from the user"""
    header = {"Authorization": "Bearer " + token}
    territory_response = requests.get(URL+"/territories/all/", headers=header, timeout=10)
    territory_response_json = territory_response.json()
    return territory_response_json

def create_new_drone(token,territory):
    """creates a new drone

    Returns:
        token + drone
    """

    drone = {
        "name": f"Drone-{random.randint(1, 100000)}",
        "drone_type": "Unmanned Aerial Vehicle",
        "cc_range": random.randrange(5.0, 100.0),
        "flight_range": random.randrange(50.0, 500.0),
        "flight_time": random.randrange(50.0, 150.0)
    }

    header = {"Authorization": "Bearer " + token}
    response = requests.post(URL+"/drones/signup/", headers=header, params=drone, timeout=10)
    signup_json_response = response.json()

    angle = random.random()
    simulation_drone = {
        "drone": signup_json_response["drone"],
        "token": signup_json_response["token"],
        "geo_json": territory["geo_json"],
        "speed": random.uniform(0.00001, 0.000001),
        "direction": (math.cos(angle), math.sin(angle)),
        "lat": territory["lat"],
        "lon": territory["lon"],
        "update_count": 0,
        "last_lat": territory["lat"],
        "last_lon": territory["lon"]
    }
    return simulation_drone


def simulate():
    """simulates drones in a loop
    """
    time.sleep(3)
    print("simulation start")
    first_event = True
    token = ''
    territories = None
    drone_amounts = []
    drones_created = []
    drones = []

    while True:
        if token == '':
            try:
                token = login()
            except ConnectionError:
                print("Login with demo admin account failed. retrying in 3 sec")
                time.sleep(3)
                continue
        try:
            if territories is None:
                try:
                    drone_amounts = []
                    drones_created = []
                    territories = get_territories_from_user(token)
                    for _ in territories:
                        drone_amounts.append(random.randint(5, 20))
                        drones_created.append(0)
                except ConnectionError:
                    print("Territorries of the demo account could not be retrieved. retrying in 3 sec")
                    time.sleep(3)
                    continue

            for i, territory in enumerate(territories):
                if drones_created[i] < drone_amounts[i]:
                    try:
                        new_drone = create_new_drone(token, territory)
                        drones.append(new_drone)
                        drones_created[i] += 1
                        print(f"{drones_created[i]}/{drone_amounts[i]} drones created for {territory['name']}")
                    except ConnectionError:
                        print("Could not create drone. retrying in 3 sec")
                        time.sleep(3)
                        continue
            done = True
            for i, _ in enumerate(drones_created):
                if drones_created[i] != drone_amounts[i]:
                    done = False
                    break
            if done:
                break
        except HTTPException:
            print("Token most likely expired. Renewing token.")
            continue

    print("All drones successfully created")

    last_execution = datetime.now()
    next_update = datetime.now()
    delta = timedelta(minutes=10)
    curr_time = timedelta(seconds=0)
    secound = timedelta(seconds=1)
    updating = True
    while True:
        delta_time = datetime.now() - last_execution
        curr_time += delta_time
        last_execution = datetime.now()
        if curr_time >= secound:
            curr_time -= secound
            print("looping")
            if datetime.now() >= next_update:
                updating = True
                next_update = datetime.now() + delta

            for drone_entry in drones:
                geo_json = drone_entry["geo_json"]
                direction = drone_entry["direction"]
                speed = drone_entry["speed"]

                new_lat = drone_entry["lat"] + direction[1] * speed * delta_time.seconds
                new_lon= drone_entry["lon"] + direction[0] * speed * delta_time.seconds

                new_point = Point(new_lon, new_lat)

                found = False
                if geo_json["type"] == "Feature":
                    polygon = shape(geo_json['geometry'])
                    found = polygon.contains(new_point)
                elif geo_json["type"] == "FeatureCollection":
                    for feature in geo_json['features']:
                        polygon = shape(feature['geometry'])
                        if polygon.contains(new_point):
                            found = True
                            break

                if not found: #not in polygon -> just turn randomly
                    new_angle = random.uniform(0, 6.28318530718)
                    dir_x = 1 * math.cos(new_angle)
                    dir_y = 1 * math.sin(new_angle)

                    drone_entry["direction"] = (dir_x, dir_y)
                else: #in poly -> do the movement
                    drone_entry["lat"] = new_lat
                    drone_entry["lon"] = new_lon

                if updating:
                    distance = math.hypot(drone_entry["last_lon"] - drone_entry["lon"],
                            drone_entry["last_lat"] - drone_entry["lat"])

                    drone_id = drone_entry["drone"]["id"]
                    new_update = {
                        "drone_id": int(drone_id),
                        "timestamp": datetime.now(),
                        "lon": float(drone_entry["lon"]),
                        "lat":  float(drone_entry["lat"]),
                        "flight_range":  float(drone_entry["drone"]["flight_range"]) - distance,
                        "flight_time":  float(drone_entry["drone"]["flight_time"]) - (1/6),
                        "current_drone_token": drone_entry["token"]
                    }

                    print(f"Sending POST request for drone {drone_id}")
                    update_success = False
                    while update_success is not True:
                        try:
                            requests.post(URL + "/drones/send-update/", params=new_update, timeout=10)
                            update_success = True
                        except HTTPException:
                            print("POST updade request failed. retrying in 3 sec")
                            time.sleep(3)

                    if random.random() <= 0.5:#CHANCE_OF_EVENT: #event happens as well
                        print(f"Events triggered for drone {drone_id}")
                        first_event = False
                        #pick random file
                        try:
                            file_name = random.choice(os.listdir(ASSETS))
                            path = os.path.join(ASSETS, file_name)

                            print("Starting AI")
                            results = ai_prediction(path)
                            print("AI DONE")
                            print(results)
                            for result in results:
                                event = {
                                "drone_id": drone_entry["drone"]["id"],
                                "timestamp": datetime.now(),
                                "lon": drone_entry["lon"],
                                "lat": drone_entry["lat"],
                                "event_type": result.event_type,
                                "confidence": result.confidence,
                                "current_drone_token": drone_entry["token"],
                                "csv_file_path": None,
                                }
                                #might be needed
                                print("Image conversion")
                                img_mem = BytesIO()
                                result.picture.save(img_mem, 'JPEG', quality=70)
                                img_mem.seek(0)
                                files = {'file_raw': open(path, "rb"), 'file_predicted': img_mem}
                                print("Sending POST request for event")
                                header = {"accept": "application/json"}
                                event_response = requests.post(URL + "/drones/send-event/", headers=header, params=event, files=files, timeout=10)
                                print("EVENT SEND")
                                print(event_response.text)
                        except Exception as event_error:
                            print("Event could not be generated")
                            print(event_error)
            updating = False
