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
from ..dependencies.email import *
from ..dependencies.authentication import *
from classes import *

router = APIRouter()

@router.post("email/verify/", status_code=status.HTTP_200_OK)
async def verify_email(token: str):
    invalid_token_exception = HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Token invalid",
        )

    exists = mail_verif_table.check_token(token)
    if not exists:
       raise invalid_token_exception

    try:
        token_email = await get_email_from_token(token)
    except HTTPException as e:
        if e.status_code == status.HTTP_406_NOT_ACCEPTABLE: #expired
            mail_from_token = mail_verif_table.get_mail_by_token(token)
            success = await send_signup_email(mail_from_token) #placeholder
            if success:
                mail_verif_table.store_token(mail_from_token,new_token, update=True)
            #change token in db
            #if sending successfull...
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="Token expired. A new email is on it's way",
            )
        else:
            raise invalid_token_exception
    db_token = mail_verif_table.get_token_by_mail(token_email)

    #delete token from db
    user = get_user(token_email)
    user.verified_email = True
    return {"message": "Email successfully verified"}