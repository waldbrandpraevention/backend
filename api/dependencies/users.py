from pydantic import BaseModel
from fastapi import Depends, HTTPException, status
from enum import Enum
from .classes import User, UserWithSensitiveInfo, Allert
from .authentication import oauth2_scheme, verify_password, get_email_from_token
from database import users_table
from datetime import datetime, timedelta

def get_user(email: str) -> UserWithSensitiveInfo | None:
    """Creates a user object from the information in the db

    Args:
        email (str): Email of the user

    Returns:
        User: User object filled with the user information
        None: if no user exists with the given email
    """

    return users_table.get_user(email)

def authenticate_user(email: str, password: str):
    """Creates a user if the given password matches the users password

    Args:
        email (str): Email of the user
        password (str): Plaintext password

    Returns:
        User: Authenticated user
        None: If user does not exists or the passowrd is wrong
    """
    user = get_user(email)
    if user and verify_password(password, user.hashed_password):
        return user
    return None

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """_summary_

    Args:
        token (str, optional): _description_. Defaults to Depends(oauth2_scheme).

    Raises:
        credentials_exception: Raises error if the token is invalid
        disabled_exception: Raises error if the user is disabled
        email_verification_exception: Raises orror if the email of the user did not get verified yet

    Returns:
        User: User object of the current user
    """
    disabled_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="User is disabled",
        headers={"WWW-Authenticate": "Bearer"},
    )
    email_verification_exception = HTTPException(
        status_code=status.HTTP_406_NOT_ACCEPTABLE,
        detail="Email is not verified",
    )
    email = await get_email_from_token(token)
    user = get_user(email)
    if user is None:
        raise credentials_exception
    if user.disabled:
        raise disabled_exception
    #if not user.email_verified:
        #raise email_verification_exception
    return user

async def get_user_allerts(user: User):
    #TODO add db call here or to user directly during object creation
    allerts = []
    allerts.append(Allert(content="Test allert", date=datetime.now()))
    allerts.append(Allert(content="1+1=2", date=datetime.now()))
    allerts.append(Allert(content="Dein name ist " + user.first_name + " " + user.last_name, date=datetime.now()))
    return allerts
