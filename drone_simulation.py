from database.drone_updates_table import create_drone_update, get_latest_update
from database.drones_table import get_drones
from datetime import datetime

def run_simulation():
    while True:
        drones = get_drones()
        for drone in drones:
            update = get_latest_update(drone.id)
            #ensure the drone stays in zone
            x = update.longitude + 0.00001
            y = update.latitude + 0.00001
            create_drone_update

            create_drone_update(drone_id,
                            datetime.utcnow(),
                            x,
                            y,
                            update.flight_range - 0.001,
                            update.flight_time - 0.001)

        time.sleep(1)

