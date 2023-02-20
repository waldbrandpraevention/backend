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
    login_data = {"username": admin_mail, "password": admin_password}
    login_response = requests.post(URL+"/users/login/", data=login_data)
    login_json_response = login_response.json()
    token = login_json_response["access_token"]
    return token

def get_territories_local():
    territories = territories_table.get_territories(orga_id=1)
    return territories

def create_new_drone(territory):
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
        "geo_json": territory["geo_json"],
        "speed": random.randrange(0.00001, 0.000001),
        "direction": (math.cos(angle), math.sin(angle)),
        "lat": territory["lat"],
        "lon": territory["lon"],
        "update_count": 0
    }
    return simulation_drone


def simulate():
    """simulates drones in a loop
    """
    return

    try:
        territories = get_territories_local()
        drones = []
        print("Creating drones")
        for i in territories:
            territory = territories[i]
            territory_name = territory["name"]
            drone_amount = random.randint(5, 20)
            created_drones = 0
            while created_drones < drone_amount:
                try:
                    drones.append(create_new_drone(drone_amount))
                    created_drones += 1
                    print(f"{created_drones}/{drone_amount} drones created for {territory_name}")
                except Exception as err:
                    print("Simulation Error: Unable to create drone. Retrying in 5sec")
                    print(err)
                    time.sleep(5)
    except Exception as errr:
        print("Error")
        print(errr)

    print("All drones successfully created")
    last_execution = datetime.now()
    next_update = datetime.now()
    delta = timedelta(minutes=10)
    while True:
        try:
            delta_time = datetime.now() - last_execution
            last_execution = datetime.now()

            for drone_entry in drones:
                geo_json = drone_entry["geo_json"]
                direction = drone_entry["direction"]
                speed = drone_entry["speed"]

                new_lat = drone_entry["lat"] + direction[1] * speed * delta_time
                new_lon= drone_entry["lon"] + direction[0] * speed * delta_time

                new_point = Point(new_lon, new_lat)

                found = False

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

                if datetime.now() >= next_update:
                    print("Updating drones")
                    next_update = datetime.now() + delta

                    distance = math.hypot(drone_entry["last_update"]["lon"] - drone_entry["lon"],
                            drone_entry["last_update"]["lat"] - drone_entry["lat"])

                    drone_id = drone_entry["drone"]["id"]
                    new_update = {
                        "drone_id": drone_id,
                        "timestamp": datetime.now(),
                        "lon": drone_entry["lon"],
                        "lat": drone_entry["lat"],
                        "flight_range": drone_entry["drone"]["flight_range"] - distance,
                        "flight_time": drone_entry["drone"]["flight_time"] - (60/10)
                    }

                    print(f"Sending POST request for drone {drone_id}")
                    try:
                        response = requests.post(URL + "/drones/send-update/", params=new_update)
                        response_json = response.json()
                        print(f"POST request for drone {drone_id} completed with status: {response_json['message']}")
                    except Exception as update_error:
                        print("POST request failed")
                        print(update_error)

                    if random.random() <= CHANCE_OF_EVENT: #event happens as well
                        print(f"Events triggered for drone {drone_id}")
                        #pick random file
                        try:
                            file_name = random.choice(os.listdir(ASSETS))
                            path = os.path.join(ASSETS, file_name)

                            print("Starting AI")
                            try:
                                results = ai_prediction(path)
                                for result in results:
                                    try:
                                        print("Event found")
                                        event = {
                                        "drone_id": drone_entry["drone"]["id"],
                                        "timestamp": datetime.now(),
                                        "longitude": drone_entry["lon"],
                                        "latitude": drone_entry["lat"],
                                        "event_type": result.event_type,
                                        "confidence": result.confidence,
                                        "csv_file_path": None,
                                        }
                                        #might be needed
                                        print("Image conversion")
                                        img_io = StringIO()
                                        result.picture.save(img_io, 'JPEG', quality=70)
                                        img_io.seek(0)
                                        files = {'file_raw:': open(path, "rb"), 'file_predicted:': img_io}
                                        header = {"Authorization:" "Bearer " + drone_entry["token"]}
                                        print("Sending POST request for event")
                                        event_response = requests.post(URL + "drones/send-event/", params=event, headers=header, files=files)
                                    except Exception as specific_event_error:
                                        print("Event could not be send")
                                        print(specific_event_error)
                            except Exception as ai_error:
                                print("AI prediction failed")
                                print(ai_error)
                        except Exception as event_error:
                            print("Event could not be generated")
                            print(event_error)
        except Exception as err2:
            print("Simulation error:\n")
            print(err2)
