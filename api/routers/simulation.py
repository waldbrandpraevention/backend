"""functions for the simulation api"""

from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter()


@router.get("/simulation/all-drones/", status_code=status.HTTP_200_OK, response_model=list[Zone])
async def read_zones_all():
    """API call to get all simulation drones.

    Returns:
        DronesForSimulation[]: List of drones.
    """

    drones = []

    #load the drones
    return get_current_wind()