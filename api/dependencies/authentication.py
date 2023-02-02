from fastapi import APIRouter

from datetime import datetime, timedelta
from fastapi import Depends, FastAPI, HTTPException, status, Request, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from database import users_table

import random
from database import mail_verif_table
from validation import *
from .classes import Token, TokenData


#secret key generated with: openssl rand -hex 32
#should not be included dn the public repo in the final build
SECRET_KEY = "cbdc851fece93e7b1a3bf9ca16c9ce62939e22f668866c875d294363e2530b27"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS = 24
DRONE_TOKEN_EXPIRE_WEEKS = 100

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

router = APIRouter()

def verify_password(plain_password, hashed_password):
    """Checks if a plain password matches a given hash

    Args:
        plain_password (str): Plain text password
        hashed_password (str): hashed password

    Returns:
        bool: True if the hashes match
    """
    return pwd_context.verify(plain_password, hashed_password)
    
def get_password_hash(password):
    """Returns the hash of the given pssward

    Args:
        password (str): Plain text password

    Returns:
        str: hash
    """
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta):
    """Creates an access token with an expiration time

    Args:
        data (dict): Data to encode

        expires_delta (timedelta): Time till expiration

    Returns:
        str: token
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_email_from_token(token: str = Depends(oauth2_scheme), allow_expired: bool = False):
    """Returns the email in the token (works for drone name as well)

    Args:
        token str: Usertoken to decode

    Raises:
        HTTPException: Raises error if the token has no email or the token is invalid or expired

    Returns:
        str: email that is embedded in the token
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_signature": not allow_expired})

        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token has no information",
            )
        token_data = TokenData(email=email)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Token is expired",
        )
    return token_data.email