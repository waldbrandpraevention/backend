import os
import sqlite3

from fastapi import Depends, FastAPI, HTTPException, status
import random
from fastapi.middleware.cors import CORSMiddleware

from threading import Thread

from simulation.sim import simulate
from api.dependencies.authentication import get_password_hash
from api.dependencies.emails import send_email
from api.dependencies.weather import wind_update
from api.dependencies.classes import Organization, UserWithSensitiveInfo
from api.routers import emails, users, zones, drones, weather, simulation
from database import users_table, organizations_table
from database import drone_events_table
from database import zones_table
from database.database import create_table, initialise_spatialite
from database.drone_events_table import CREATE_DRONE_EVENT_TABLE
from database import orga_zones_table
from database.drone_updates_table import CREATE_DRONE_DATA_TABLE
from database.organizations_table import CREATE_ORGANISATIONS_TABLE
from database.users_table import CREATE_USER_TABLE
from database.zones_table import CREATE_ZONE_TABLE

app = FastAPI()
app.include_router(users.router)
app.include_router(emails.router)
app.include_router(zones.router)
app.include_router(drones.router)
app.include_router(weather.router)
app.include_router(simulation.router)

# CORS https://fastapi.tiangolo.com/tutorial/cors/
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def create_default_user():
    # Save default user only if env var is set
    if os.getenv("ADMIN_MAIL") is not None \
            and os.getenv("ADMIN_PASSWORD") is not None \
            and os.getenv("ADMIN_ORGANIZATION") is not None:
        try:
            organization = organizations_table.create_orga(organame=os.getenv("ADMIN_ORGANIZATION"), orga_abb=os.getenv("ADMIN_ORGANIZATION"))
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
    """ for demo set
        long=12.68895149
        lat=52.07454738
    """
    if os.getenv("DEMO_LONG") is not None \
            and os.getenv("DEMO_LAT") is not None:
        
        drone_events_table.insert_demo_events(12.559776306152344,52.189299066349946,2)
        drone_events_table.insert_demo_events(12.559776306152344,50.189299066349946,3)
        drone_events_table.insert_demo_events(float(os.getenv("DEMO_LONG")),float(os.getenv("DEMO_LAT")))
    
    print("drone_events done")

def load_zones_from_geojson():
    """ for demo set
        Landkreis Potsdam-Mittelmark
    """
    if os.getenv("GEOJSON_PATH") is not None:
        path = os.path.realpath(os.path.dirname(__file__))
        path+=os.getenv("GEOJSON_PATH")
        added_zones = zones_table.load_from_geojson(path)
        print(f'Zones added: {added_zones}')
        
        if os.getenv("DEMO_DISTRICT") is not None \
                and os.getenv("ADMIN_ORGANIZATION") is not None:
            fetched_zones = zones_table.get_zone_of_by_district(os.getenv("DEMO_DISTRICT"))
            for zone in fetched_zones:
                try:
                    orga_zones_table.link_orgazone(1,zone.id)
                except sqlite3.IntegrityError:
                    pass

    print("zones done")

def main():
    initialise_spatialite()
    create_table(CREATE_ORGANISATIONS_TABLE)
    create_table(CREATE_USER_TABLE)
    create_table(CREATE_DRONE_EVENT_TABLE)
    create_table(CREATE_ZONE_TABLE)
    create_table(CREATE_DRONE_DATA_TABLE)
    create_table(orga_zones_table.CREATE_ORGAZONES_TABLE)
    create_default_user()
    create_drone_events()
    load_zones_from_geojson()

    #make sure this actually works
    simulation_thread = Thread(target = simulate)
    weather_thread.start()


main()

@app.get("/")
async def root():
    n1 = random.randint(0,100)
    n2 = random.randint(0,100)
    raise HTTPException(
                status_code=status.HTTP_418_IM_A_TEAPOT,
                detail="Random addition: " + str(n1) + " + " + str(n2) + " = " + str(n1 +n2),
            )

@app.get("/test")
async def test(input: str):
    return {"message": input}


@app.get("/test-mail/")
async def test_mail(reciever: str, subject: str, message: str):
    return await send_email(reciever, subject, message)