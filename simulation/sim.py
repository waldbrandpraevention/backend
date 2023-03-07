"""functions for the simulation"""
import asyncio
import json
import pickle
import time
import os
import random
import math
from typing import List
from PIL.JpegImagePlugin import JpegImageFile
from io import BytesIO
from datetime import datetime, timedelta
import aiohttp
import requests
from shapely.geometry import shape, Point
from fastapi import HTTPException

from api.dependencies.classes import DroneEvent
from .cv import ai_prediction

ASSETS = "./simulation/assets/raw/"
URL = os.getenv("DOMAIN_API")
admin_mail = os.getenv("ADMIN_MAIL")
admin_password = os.getenv("ADMIN_PASSWORD")
CHANCE_OF_EVENT = os.getenv("SIMULATION_EVENT_CHANCE")
SIMULATION_UPDATE_FREQUENCY = int(os.getenv("SIMULATION_UPDATE_FREQUENCY"))
SIMULATION_DRONE_SPEED_MIN = float(os.getenv("SIMULATION_DRONE_SPEED_MIN"))
SIMULATION_DRONE_SPEED_MAX = float(os.getenv("SIMULATION_DRONE_SPEED_MAX"))
post_req_semaphore = asyncio.Semaphore(10)

async def login():
    """login for the simulation"""
    login_data = {"username": admin_mail, "password": admin_password}
    login_response = requests.post(URL+"/users/login/", data=login_data, timeout=10)
    login_json_response = login_response.json()
    token = login_json_response["access_token"]
    return token

async def get_territories_from_user(token):
    """gets the territories from the user"""
    header = {"Authorization": "Bearer " + token}
    territory_response = requests.get(URL+"/territories/all/", headers=header, timeout=10)
    territory_response_json = territory_response.json()
    return territory_response_json

async def create_new_drone(token,territory):
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

    angle = 2 * math.pi * random.random()
    simulation_drone = {
        "drone": signup_json_response["drone"],
        "token": signup_json_response["token"],
        "geo_json": territory["geo_json"],
        "speed": random.uniform(SIMULATION_DRONE_SPEED_MIN, SIMULATION_DRONE_SPEED_MAX),
        "direction": (math.cos(angle), math.sin(angle)),
        "lat": territory["lat"],
        "lon": territory["lon"],
        "update_count": 0,
        "last_lat": territory["lat"],
        "last_lon": territory["lon"]
    }
    return simulation_drone

async def generate_drones():
    token = ''
    territories = None
    drone_amounts = []
    drones_created = []
    drones = []

    while True:
        if token == '':
            try:
                token = await login()
            except Exception:
                print("Login with demo admin account failed. retrying in 3 sec")
                await asyncio.sleep(3)
                continue
        try:
            if territories is None:
                try:
                    drone_amounts = []
                    drones_created = []
                    territories = await get_territories_from_user(token)
                    for _ in territories:
                        drone_amounts.append(40)#random.randint(5, 20))
                        drones_created.append(0)
                except Exception:
                    print("Territorries of the demo account could not be retrieved. retrying in 3 sec")
                    await asyncio.sleep(3)
                    continue

            for i, territory in enumerate(territories):
                if drones_created[i] < drone_amounts[i]:
                    try:
                        new_drone = await create_new_drone(token, territory)
                        drones.append(new_drone)
                        drones_created[i] += 1
                        print(f"{drones_created[i]}/{drone_amounts[i]} drones created for {territory['name']}")
                    except Exception:
                        print("Could not create drone. retrying in 3 sec")
                        await asyncio.sleep(3)
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
            token=''
            continue

    print("All drones successfully created")
    return drones

async def post_update(updates, loop:asyncio.BaseEventLoop):
    """sends an update for a drone"""

    for drone_entry in updates:
        distance = math.hypot(drone_entry["last_lon"] - drone_entry["lon"],
                            drone_entry["last_lat"] - drone_entry["lat"])

        drone_id = drone_entry["drone"]["id"]
        datetime_now = datetime.now()
        unix_timestamp = int(datetime.timestamp(datetime_now))
        new_update = {
            "drone_id": int(drone_id),
            "unixtimestamp": unix_timestamp,
            "lon": float(drone_entry["lon"]),
            "lat":  float(drone_entry["lat"]),
            "flight_range":  float(drone_entry["drone"]["flight_range"]) - distance,
            "flight_time":  float(drone_entry["drone"]["flight_time"]) - (SIMULATION_UPDATE_FREQUENCY/60),
            "current_drone_token": drone_entry["token"]
        }
        loop.create_task(send_update(new_update))
        


async def send_update(drone_update):
    try:
        drone_id = drone_update['drone_id']
        print(f"Sending POST request for drone {drone_id}")
        async with post_req_semaphore:
            async with aiohttp.ClientSession() as session:
                async with session.post(URL + "/drones/send-update/",
                                        params=drone_update,
                                        timeout=10) as response:
                    if response.status == 200:
                        print(f"Update for drone {drone_id} sent")
                    else:
                        text = await response.text()
                        print(text)
   
    except aiohttp.ServerTimeoutError:
        print('server down?')

    except Exception as exception:
        print(exception)
        print(f"Could not send update for drone {drone_id}")

async def post_event(events,loop:asyncio.BaseEventLoop):
    """sends an event"""

    for drone_entry in events:
        print(f"Events triggered for drone {drone_entry['drone']['id']}")
        datetime_now = datetime.now()
        unix_timestamp = int(datetime.timestamp(datetime_now))
        #pick random file
        try:
            file_name = random.choice(os.listdir(ASSETS))
            path = os.path.join(ASSETS, file_name)

            print("Starting AI")
            results,image = ai_prediction(path)
            print("AI DONE")
            print(results)
            events = []
            drone_id = drone_entry["drone"]["id"]
            current_drone_token=drone_entry["token"],
            for result in results:
                drone_event = {
                    'drone_id' : drone_entry["drone"]["id"],
                    'unixtimestamp':unix_timestamp,
                    'lon':drone_entry["lon"],
                    'lat':drone_entry["lat"],
                    'event_type':result.event_type,
                    'confidence':result.confidence
                }
                events.append(drone_event)
                #might be needed
            loop.create_task(send_events(events, path, image, drone_id, current_drone_token))
        except Exception:
            print("Event could not be send. skipping event")

async def send_events(events: List[dict], path, image:JpegImageFile, drone_id:int, current_drone_token):
    print("Image conversion")
    img_mem = BytesIO()
    image.save(img_mem, 'JPEG', quality=70)
    img_mem.seek(0)    

    print("Sending POST request for event")
    with open(path, "rb") as file_raw:
        for event in events:
            try:
                async with post_req_semaphore:
                    async with aiohttp.ClientSession() as session:
                        form = aiohttp.FormData()
                        for fieldname, fieldval in event.items():
                            form.add_field(fieldname,fieldval)
                        form.add_field('token',current_drone_token)
                        form.add_field('file_raw', file_raw)
                        form.add_field('file_predicted', img_mem)
                        
                        async with session.post(URL + "/drones/send-event/", data= form, timeout=10) as response:
                            if response.status == 200:
                                print(f"Update for drone {drone_id} sent")
                            else:
                                text = await response.text()
                                print(text)

            except aiohttp.ServerTimeoutError:
                print('server down?')

            except Exception as exception:
                print(exception)
                print(f"Could not send event for drone {drone_id}")



async def is_in_poly(geo_json, lon, lat):
    """checks of a point is in a geo_json polygon"""
    new_point = Point(lon, lat)

    if geo_json["type"] == "Feature":
        polygon = shape(geo_json['geometry'])
        return polygon.contains(new_point)
    elif geo_json["type"] == "FeatureCollection":
        for feature in geo_json['features']:
            polygon = shape(feature['geometry'])
            if polygon.contains(new_point):
                return True

    return False

def start_simulation():
    """starts the simulation"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(simulate())



async def simulate():
    """simulates drones in a loop
    """
    await asyncio.sleep(3)
    print("simulation start")
    loop = asyncio.get_event_loop()

    drones = await generate_drones()

    last_execution = datetime.now()
    next_update = datetime.now()
    updade_delta =  timedelta(seconds=SIMULATION_UPDATE_FREQUENCY)
    loop_delta = timedelta(seconds=math.ceil(SIMULATION_UPDATE_FREQUENCY / 10))
    send_update_bool = True
    while True:
        diff = datetime.now() - last_execution
        if diff < loop_delta:
            await asyncio.sleep(loop_delta.seconds -  diff.seconds)
        last_execution = datetime.now()

        if datetime.now() >= next_update:
            send_update_bool = True
            next_update = datetime.now() + updade_delta
        else:
            send_update_bool = False

        updates = []
        events = []
        for drone_entry in drones:
            await get_new_lat_lon(drone_entry,loop_delta)

            if send_update_bool:
                updates.append(drone_entry)
                if random.random() <= float(CHANCE_OF_EVENT): #event happens as well
                    events.append(drone_entry)

        loop.create_task(post_update(updates,loop))
        loop.create_task(post_event(events,loop))


async def get_new_lat_lon(drone_entry,loop_delta,recursion_index=0):

    if recursion_index > 10:
        return
    
    geo_json = drone_entry["geo_json"]
    angle = 2 * math.pi * random.random()
    direction = (math.cos(angle), math.sin(angle))
    speed = drone_entry["speed"]

    new_lat = drone_entry["lat"] + direction[1] * speed * loop_delta.seconds
    new_lon= drone_entry["lon"] + direction[0] * speed * loop_delta.seconds

    if await is_in_poly(geo_json, new_lon, new_lat):
        drone_entry["lat"] = new_lat
        drone_entry["lon"] = new_lon
        return
    else:
        recursion_index += 1
        await get_new_lat_lon(drone_entry,loop_delta,recursion_index)