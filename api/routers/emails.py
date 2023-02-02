from fastapi import APIRouter

from datetime import datetime, timedelta
from enum import Enum
from fastapi import Depends, FastAPI, HTTPException, status, Request, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from database import users_table

import random
from database import mail_verif_table
from validation import *
from classes import *

from ..dependencies.authentication import (
    send_token_email
    )

router = APIRouter()

@router.post("email/verify/", status_code=status.HTTP_200_OK)
async def verify_email(token: str):
    invalid_token_exception = HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Token invalid",
        )

    try:
        token_email = await get_email_from_token(token, False)
    except HTTPException as e:
        if e.status_code == status.HTTP_406_NOT_ACCEPTABLE: #expired
            mail_from_token = await get_email_from_token(token, True)
            await send_token_email(mail_from_token)
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="Token expired. A new email is on it's way",
            )
        else:
            raise invalid_token_exception
   
    user = get_user(token_email)
    user.verified_email = True
    return {"message": "Email successfully verified"}