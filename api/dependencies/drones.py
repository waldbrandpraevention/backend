from database import drones_table
from database import drone_updates_table as drone_data_table

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

async def get_current_drone(token: str = Depends(oauth2_scheme)):
    """Returns the current drone

    Args:
        token (str, optional): _description_. Defaults to Depends(oauth2_scheme).

    Raises:
        credentials_exception: Raises error if the token is invalid
        disabled_exception: Raises error if the user is disabled
        email_verification_exception: Raises orror if the email of the user did not get verified yet

    Returns:
        User: User object of the current user
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token data is invalid",
        headers={"WWW-Authenticate": "Bearer"},
    )
    name = await get_email_from_token(token) #returns name as well
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