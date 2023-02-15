"""functions for the simulation api"""
import os
import random
from fastapi import APIRouter, Depends, HTTPException, status
from ..dependencies.classes import DroneForSimulation
from ..dependencies.drones import generate_drone_token
from database import drones_table, zones_table

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
        zones = zones_table.get_zone_of_by_district(os.getenv("DEMO_DISTRICT"))
        
        for d in drones:
            random = randrange(0, len(zones) - 1)
            angle = random()
            d_sim = DroneForSimulation( 
                drone = d,     
                token = generate_drone_token(d.id),
                geo_json = zone[random].geo_json,
                speed = 0.0001,
                direction = (cos(angle), sin(angle)),
                lat = zones[random].lat,
                lon = zones[random].lan
            )
            sim_drones.append(d_sim)
    except Exception as e:
        print(e)
    return sim_drones