import os

from fastapi import Depends, FastAPI, HTTPException, status
import random
from fastapi.middleware.cors import CORSMiddleware

from api.dependencies.authentication import get_password_hash
from api.dependencies.classes import Organization, UserWithSensitiveInfo
from api.routers import email, users, zones, drones
from database import users_table, organizations
from database.database import create_table
from database.organizations import CREATE_ORGANISATIONS_TABLE
from database.users_table import CREATE_USER_TABLE

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
        organization = organizations.create_orga(organame=os.getenv("ADMIN_ORGANIZATION"), orga_abb=os.getenv("ADMIN_ORGANIZATION"))
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
    create_default_user()


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