"""functions for user api"""
from datetime import datetime, timedelta
from typing import List
from fastapi import Depends, HTTPException, status
from api.dependencies.drones import get_drone_events
from database import users_table, organizations_table
from validation import (validate_email,
                        validate_first_name,
                        validate_last_name,
                        validate_organization,
                        validate_password,
                        validate_permission)
from .classes import DroneEvent, Permission, User, UserWithSensitiveInfo, Allert
from .authentication import get_password_hash, oauth2_scheme, verify_password, get_email_from_token

def get_user(email: str) -> UserWithSensitiveInfo | None:
    """Creates a user object from the information in the db

    Args:
        email (str): Email of the user

    Returns:
        User: User object filled with the user information
        None: if no user exists with the given email
    """

    return users_table.get_user(email)

def get_all_users(orga_id: int) -> List[User]:
    """fetches all users which are linked to the given organization

    Args:
        orga_id (int): orga the users are linked to.

    Returns:
        List[User]: list of User objects
    """

    return users_table.get_all_users(orga_id)

def get_user_by_id(user_id: int) -> UserWithSensitiveInfo | None:
    """fetches the user object by its id.

    Args:
        user_id (int): id of the user

    Returns:
        User: User object
        None: if no user exists with the given id
    """

    return users_table.get_user_by_id(user_id)

def authenticate_user(email: str, password: str):
    """Returns user object if the given password matches the users password

    Args:
        email (str): Email of the user
        password (str): Plaintext password

    Returns:
        User: Authenticated user
        None: If user does not exists or the passowrd is wrong
    """
    user = get_user(email)
    if user is not None and verify_password(password, user.hashed_password):
        return user
    return None

async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserWithSensitiveInfo :
    """Returns the user object of the current user

    Args:
        token (str, optional): _description_. Defaults to Depends(oauth2_scheme).

    Raises:
        credentials_exception: Raises error if the token is invalid
        disabled_exception: Raises error if the user is disabled
        email_verification_exception: Raises orror if the email of the user did not get verified yet

    Returns:
        UserWithSensitiveInfo: User object of the current user
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token data is invalid",
        headers={"WWW-Authenticate": "Bearer"},
    )
    disabled_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="User is disabled",
        headers={"WWW-Authenticate": "Bearer"},
    )
    # email_verification_exception = HTTPException(
    #     status_code=status.HTTP_406_NOT_ACCEPTABLE,
    #     detail="Email is not verified",
    # )
    email = await get_email_from_token(token)
    user = get_user(email)
    if user is None:
        raise credentials_exception
    if user.disabled:
        raise disabled_exception
    # if not user.email_verified:
    #     raise email_verification_exception
    return user

async def get_user_allerts(user: User) -> List[Allert]:
    """
    ONLY FOR TESTING PURPOSES
    fetches all events from the last 24 hours and generates a string for each event.

    Args:
        user (User): user of which organization the events should be fetched.

    Returns:
        List[Allert]: list of allerts.
    """
    events = await get_drone_events(user.organization.id,
                           datetime.utcnow() - timedelta(days=1)
    )
    allerts = []
    for event in events:
        content = await generate_event_string(event)
        allerts.append(Allert(content=content, date=event.timestamp))

    return allerts

async def generate_event_string(event:DroneEvent):
    """
    generates a string for an event.

    Args:
        event (DroneEvent): the event to generate the string for.

    Returns:
        str: the generated string.
    """
    return f'''{event.event_type.name} spotted at
    Lon: {event.lon}
    Lat: {event.lat}
    with a confidence of {event.confidence}%'''

async def update_user(user_to_update:User,
                  email: str | None=None,
                  password: str| None=None,
                  first_name: str| None=None,
                  last_name: str| None=None,
                  organization_name: str| None=None,
                  permission: int | None=None,
                  disabled: bool |None=None,
                  email_verified:bool|None=None
                  ) -> bool:
    """update attributes of a user in the database.
        generates sql query based on the given parameters.

        example:
            update_user(user, email="new_email", password="new_password")
            set_sql = "email = ?, password = ?"
            valarr = ["new_email", hashed_pw]


    Args:
        user_to_update (User): user to update
        email (str | None): new email. Defaults to None.
        password (str | None): new unhashed password. Defaults to None.
        first_name (str | None): new first_name. Defaults to None.
        last_name (str | None): new last_name. Defaults to None.
        organization_name (str | None, optional): new organization_name. Defaults to None.
        permission (int | None, optional): updated permission. Defaults to None.
        disabled (bool | None, optional): updated disabled boolean. Defaults to None.
        email_verified (bool | None, optional): updated email_verified boolean. Defaults to None.

    Raises:
        HTTPException: if one or more parameters fail validation.
        HTTPException: if there is nothing to update.
        HTTPException: if the update fails.

    Returns:
        boolean: True if update was successful.
    """
    errors = []
    update_sql_dictr = {}
    if email and email != user_to_update.email:
        if get_user(email):
            errors.extend("This email is already assosiated with an existing account")
        else:
            errors.extend(validate_email(email))
            update_sql_dictr[users_table.UsrAttributes.EMAIL] = email
    if password:
        errors.extend(validate_password(password))
        hashed_pw = get_password_hash(password)
        update_sql_dictr[users_table.UsrAttributes.PASSWORD] = hashed_pw
    if first_name and first_name != user_to_update.first_name:
        errors.extend(validate_first_name(first_name))
        update_sql_dictr[users_table.UsrAttributes.FIRST_NAME] = first_name
    if last_name and last_name != user_to_update.last_name:
        errors.extend(validate_last_name(last_name))
        update_sql_dictr[users_table.UsrAttributes.LAST_NAME] = last_name
    if organization_name and organization_name != user_to_update.organization.name:
        errors.extend(validate_organization(organization_name))
        organization_obj = organizations_table.get_orga(organization_name)
        if not organization_obj:
            errors.append('orga doesnt exist.')
        else:
            update_sql_dictr[users_table.UsrAttributes.ORGA_ID] = organization_obj.id
    if permission and permission != user_to_update.permission.value:
        errors.extend(validate_permission(permission))
        update_sql_dictr[users_table.UsrAttributes.PERMISSION] = permission
    if disabled is not None and disabled != user_to_update.disabled:
        update_sql_dictr[users_table.UsrAttributes.DISABLED] = disabled
    if email_verified is not  None and email_verified != user_to_update.email_verified:
        update_sql_dictr[users_table.UsrAttributes.EMAIL_VERIFIED] = email_verified

    if len(errors) > 0:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail=errors,
        )

    if len(update_sql_dictr)==0:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail='Nothing to update.',
        )

    set_sql =""
    valarr= []
    for col_name, value in update_sql_dictr.items():
        set_sql+= f'{col_name}=?,'
        valarr.append(value)
    set_sql = set_sql[:-1]

    success = users_table.update_user_withsql(user_to_update.id,set_sql,valarr)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Couldnt update the user.',
        )

    return True

async def is_admin(user:User)->bool:
    """checks wether user has admin rights.

    Args:
        user (User): user to check.

    Raises:
        HTTPException: if not an admin.

    Returns:
        bool: True if is admin.
    """
    if user.permission != Permission.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You dont have the permission to do this (Not an admin).",
        )

    return True
