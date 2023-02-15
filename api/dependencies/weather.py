import requests
import json
from datetime import date
from .classes import WindInfo
import time
import asyncio

wind = []

def load_sources():
    f = open('./stations.txt', 'r')
    return f.readlines()

def get_wind():
    wind_info = []
    ids = load_sources()
    #curr_date = date.today()
    for id in ids:
        payload = {'dwd_station_id': id.strip().zfill(5)}
        response = requests.get("https://api.brightsky.dev/current_weather", params=payload)
        print(response.url)
        if(response.status_code == 200):
            text = response.text
            info = json.loads(text)
            lat = info["sources"][0]["lat"]
            lon = info["sources"][0]["lon"]
            speed = info["weather"]["wind_speed_10"]
            direction = info["weather"]["wind_direction_10"]

            new_info = WindInfo(
                lat = lat,
                lon = lon,
                wind_speed = speed,
                wind_direction = direction)
            wind_info.append(new_info)
    return wind_info

def wind_update():
    global wind
    last_execution = time.time()
    while(True):
        if(time.time() - last_execution > 1800 or len(wind) == 0):
            wind = get_wind()
            last_execution = time.time()

def get_current_wind():
    global wind
    return wind


