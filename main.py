from fastapi import Depends, FastAPI, HTTPException, status
import random
from fastapi.middleware.cors import CORSMiddleware
from api.routers import email, users, zones, drones
from database.database import create_table
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


def main():
    create_table(CREATE_USER_TABLE)


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