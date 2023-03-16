"""functions for the simulation api"""
import os
import random
import math
from fastapi import APIRouter, status
from database import drones_table, zones_table
from ..dependencies.classes import DroneForSimulation
from ..dependencies.drones import generate_drone_token

router = APIRouter()

@router.get("/simulation/all-drones/", status_code=status.HTTP_200_OK)
async def get_sim_drones():
    """API call to get all simulation drones.

    Returns:
        DronesForSimulation[]: List of drones.
    """
    try:
        sim_drones = []
        drones =  drones_table.get_all_drones()
        zones = zones_table.get_zone_of_district(os.getenv("DEMO_DISTRICT"))

        for drone in drones:
            rand = random.randrange(0, len(zones) - 1)
            angle = random.random()
            d_sim = DroneForSimulation(
                drone = drone,
                token = generate_drone_token(drone.id),
                geo_json = zones[rand].geo_json,
                speed = 0.0001,
                direction = (math.cos(angle), math.sin(angle)),
                lat = zones[rand].lat,
                lon = zones[rand].lan
            )
            sim_drones.append(d_sim)
    except Exception as err: # pylint: disable=broad-exception-caught
        print(err)
    return sim_drones
