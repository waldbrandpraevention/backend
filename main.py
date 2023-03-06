""" Main file for the API. """
import os
import sqlite3
import random
from threading import Thread
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from simulation.sim import simulate
from api.dependencies.authentication import get_password_hash
from api.dependencies.emails import send_email
from api.dependencies.classes import UserWithSensitiveInfo
from api.routers import emails, users, zones, drones, simulation,territories, alarm
from database import (users_table,
                      organizations_table,
                      drones_table,
                      drone_events_table,
                      zones_table)

from database.database import create_table, initialise_spatialite
from database.drone_events_table import CREATE_DRONE_EVENT_TABLE
from database.territory_zones_table import CREATE_TERRITORYZONES_TABLE, link_territory_zone
from database.territories_table import CREATE_TERRITORY_TABLE, create_territory
from database.drone_updates_table import CREATE_DRONE_DATA_TABLE
from database.drones_table import CREATE_DRONES_TABLE
from database.organizations_table import CREATE_ORGANISATIONS_TABLE
from database.users_table import CREATE_USER_TABLE
from database.zones_table import CREATE_ZONE_TABLE

app = FastAPI(  title="KIWA",
                description="test")
app.include_router(users.router)
app.include_router(emails.router)
app.include_router(zones.router)
app.include_router(drones.router)
app.include_router(simulation.router)
app.include_router(territories.router)
app.include_router(alarm.router)

# CORS https://fastapi.tiangolo.com/tutorial/cors/
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def create_default_user():
    """Creates a default user if the environment variables are set."""
    # Save default user only if env var is set
    if os.getenv("ADMIN_MAIL") is not None \
            and os.getenv("ADMIN_PASSWORD") is not None \
            and os.getenv("ADMIN_ORGANIZATION") is not None:
        try:
            organization = organizations_table.create_orga(
                organame=os.getenv("ADMIN_ORGANIZATION"),
                orga_abb=os.getenv("ADMIN_ORGANIZATION")
                )
        except sqlite3.IntegrityError:
            organization = organizations_table.get_orga(os.getenv("ADMIN_ORGANIZATION"))
        hashed_pw = get_password_hash(os.getenv("ADMIN_PASSWORD"))
        user = UserWithSensitiveInfo(email=os.getenv("ADMIN_MAIL"),
                                     first_name="Admin",
                                     last_name="Admin",
                                     hashed_password=hashed_pw,
                                     organization=organization,
                                     permission=2,
                                     disabled=0,
                                     email_verified=1)
        try:
            users_table.create_user(user)
        except sqlite3.IntegrityError:
            pass
        print("user done")

def create_drone_events():
    """ Creates drone events for demo purposes.
        set demo events with env vars DEMO_LONG and DEMO_LAT
    """
    if os.getenv("DEMO_LONG") is not None \
            and os.getenv("DEMO_LAT") is not None:

        drones_table.create_drone(
                name='Trinity F01',
                drone_type="Unmanned Aerial Vehicle",
                cc_range=7.5,
                flight_range=100.0,
                flight_time=90.0
            )
        drone_events_table.insert_demo_events(
                                            float(os.getenv("DEMO_LONG")),
                                            float(os.getenv("DEMO_LAT"))
                                            )
    print("drone_events done")

def load_zones_from_geojson():
    """ store all zones from geojson file in the database.
        link the zones, of the DEMO_DISTRICT env var, to the territory of the ADMIN_ORGANIZATION.
    """
    if os.getenv("GEOJSON_PATH") is not None:
        main_path = os.path.realpath(os.path.dirname(__file__))
        path_to_geo = os.path.join(main_path,os.getenv("GEOJSON_PATH"))
        added_zones = zones_table.add_from_geojson(path_to_geo)
        print(f'Zones added: {added_zones}')

        if os.getenv("DEMO_DISTRICT") is not None \
                and os.getenv("ADMIN_ORGANIZATION") is not None:
            fetched_zones = zones_table.get_zone_of_district(os.getenv("DEMO_DISTRICT"))
            try:
                create_territory(orga_id=1,name=os.getenv("DEMO_DISTRICT"))
            except sqlite3.IntegrityError:
                print('couldnt create territory')

            for zone in fetched_zones:
                try:
                    link_territory_zone(1,zone.id)
                except sqlite3.IntegrityError:
                    print(f'couldnt link {zone.name} to the territory')

            print("zones linked")

def main():
    """ Initialise the database and create the tables.
        Create a default user if the environment variables are set.
        Create a default territory and link zones to it, if the environment variables are set.
    """
    initialise_spatialite()
    create_table(CREATE_ORGANISATIONS_TABLE)
    create_table(CREATE_USER_TABLE)
    create_table(CREATE_ZONE_TABLE)
    create_table(CREATE_DRONES_TABLE)
    create_table(CREATE_DRONE_DATA_TABLE)
    create_table(CREATE_DRONE_EVENT_TABLE)
    create_table(CREATE_TERRITORY_TABLE)
    create_table(CREATE_TERRITORYZONES_TABLE)
    create_default_user()
    #create_drone_events()
    #create_drones()
    load_zones_from_geojson()

    #make sure this actually works
    try:
        simulation_thread = Thread(target = simulate)
        simulation_thread.start()
        #weather_thread.start()
    except Exception as err:
        print(err)


main()

@app.get("/")
async def root():
    """ Root function to check if the server is running."""
    number_one = random.randint(0,100)
    number_two = random.randint(0,100)
    raise HTTPException(
                status_code=status.HTTP_418_IM_A_TEAPOT,
                detail=f"""Random addition: {number_one}
                        {number_one} {number_one +number_two}""",
            )

@app.get("/test")
async def test(test_input: str):
    """ Test function to check if the server is running."""
    return {"message": test_input}


@app.get("/test-mail/")
async def test_mail(reciever: str, subject: str, message: str):
    """ Test function to check if the server is running."""
    return await send_email(reciever, subject, message)
