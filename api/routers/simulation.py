"""functions for the simulation api"""

from fastapi import APIRouter, Depends, HTTPException, status
from ..dependencies.classes import DroneForSimulation

router = APIRouter()


@router.get("/simulation/all-drones/", status_code=status.HTTP_200_OK)
async def read_zones_all():
    """API call to get all simulation drones.

    Returns:
        DronesForSimulation[]: List of drones.
    """

    #load the drones #todo
    drones = []
    return drones