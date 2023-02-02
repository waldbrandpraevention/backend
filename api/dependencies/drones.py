from database import drones_table
from database import drone_updates_table as drone_data_table
from .authentication import create_access_token, DRONE_TOKEN_EXPIRE_WEEKS
from datetime import datetime

async def get_all_drones():
    """Returns all drones from the db

    Returns:
        Zone[]: List of drones
    """
    drones = []
    
    drones = drones_table.get_drones()

    for drone in drones:
        drone_data = drone_data_table.get_latest_update(drone.id)
        if drone_data:
            drone.last_update = drone_data.timestamp
            #TODO Get Zone by lat and long

    return drones


async def generate_drone_token(id: int):
    """Returns a new drone token

    Returns:
        Token: new token
    """
    access_token_expires = timedelta(minutes=DRONE_TOKEN_EXPIRE_WEEKS)
    access_token = create_access_token(
        data={"sub": id}, expires_delta=access_token_expires
    )

    return access_token

async def get_drone(name: str):
    """Returns a specific drone from the db

    Returns:
        Drone: the requestesd drone
    """
    drone = drones_table.get_drone(name)
    drone_data = drone_data_table.get_latest_update(drone.id)
    if drone_data:
        drone.last_update = drone_data.timestamp
        #TODO Get Zone by lat and long

    return drone

async def get_current_drone(token: str):
    """Returns the current drone

    Args:
        token (str): token

    Returns:
        Drone: Drone object of the current drone
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token data is invalid",
        headers={"WWW-Authenticate": "Bearer"},
    )
    name = await get_email_from_token(token) #returns id as well
    drone = get_drone(name)
    if drone is None:
        raise credentials_exception

    return drone

async def get_drone_count():
    """Returns the amount of drones

    Returns:
        int: amount of drones
    """

    return len(await get_all_drones())