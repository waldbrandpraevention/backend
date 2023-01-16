import os

from fastapi import Depends, FastAPI, HTTPException, status
import random
from fastapi.middleware.cors import CORSMiddleware

from api.dependencies.authentication import get_password_hash
from api.dependencies.classes import Organization, UserWithSensitiveInfo
from api.routers import email, users, zones, drones
from database import users_table, organizations_table, drones_table, drone_updates_table, zones_table
from database.database import create_table
from database.organizations_table import CREATE_ORGANISATIONS_TABLE
from database.users_table import CREATE_USER_TABLE
from database.drones_table import CREATE_DRONES_TABLE, create_drone
from database.drone_updates_table import CREATE_DRONE_DATA_TABLE, create_drone_update
from database.zones_table import CREATE_ZONE_TABLE, create_zone

from threading import Thread 
from drone_simulation import run_simulation

app = FastAPI()
app.include_router(users.router)
app.include_router(email.router)
app.include_router(zones.router)
app.include_router(drones.router)

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
        organization = organizations_table.create_orga(organame=os.getenv("ADMIN_ORGANIZATION"), orga_abb=os.getenv("ADMIN_ORGANIZATION"))
        hashed_pw = get_password_hash(os.getenv("ADMIN_PASSWORD"))
        user = UserWithSensitiveInfo(email=os.getenv("ADMIN_MAIL"),
                                     first_name="Admin",
                                     last_name="Admin",
                                     hashed_password=hashed_pw,
                                     organization=organization,
                                     permission=2,
                                     disabled=0,
                                     email_verified=1)
        users_table.create_user(user)
        print("done")

def main():
    create_table(CREATE_ORGANISATIONS_TABLE)
    create_table(CREATE_USER_TABLE)
    #create_table(CREATE_DRONES_TABLE)
    #create_table(CREATE_DRONE_DATA_TABLE)
    create_default_user()

    #create_drone("Bob", 42, "some type", 100000, 100000, 100000)
    #create_drone("Hugo", 69, "some type", 100000, 100000, 100000)
    #create_drone("Klaus", 12345, "some type", 100000, 100000, 100000)
    #create_drone_update()

    #TODO add drones and zones and stuff here
    #t = Thread(target = run_simulation) 
    #t.start()  


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