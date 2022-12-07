from fastapi import Depends, FastAPI, HTTPException, status
import random
from api.routers import email, users
from database.database import create_table
from database.users_table import CREATE_USER_TABLE

app = FastAPI()
app.include_router(users.router)
app.include_router(email.router)

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