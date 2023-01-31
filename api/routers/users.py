"""API calls for User specific stuff"""
from datetime import timedelta
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordRequestForm
from database import users_table
from database import organizations_table
from validation import (validate_email,
                        validate_first_name,
                        validate_last_name,
                        validate_organization,
                        validate_password)
from api.dependencies.classes import Token,User,UserWithSensitiveInfo

from ..dependencies.authentication import (
    create_access_token,
    get_password_hash,
    ACCESS_TOKEN_EXPIRE_MINUTES
    )
from ..dependencies.users import (
    get_all_users,
    get_user_by_id,
    is_admin,
    update_user as update_user_func,
    get_current_user,
    authenticate_user,
    get_user_allerts,
    get_user
    )

router = APIRouter()



@router.get("/users/me/", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """API call to get the curret user we are communicating with

    Args:
        current_user (User, optional): User. Defaults to Depends(get_current_user).

    Returns:
        User: Current user with only the basic infos (no password)
    """
    return current_user

@router.post("/users/delete/", status_code=status.HTTP_200_OK)
async def delete_users( user_id:int,
                        current_user: User = Depends(get_current_user)):
    """API call to get the curret user we are communicating with

    Args:
        current_user (User, optional): User. Defaults to Depends(get_current_user).

    Returns:
        User: Current user with only the basic infos (no password)
    """
    await is_admin(current_user)
    if users_table.delete_user(user_id):
        return {"message": "success"}

    return {"message": "couldnt create user."}

@router.get("/users/me/allerts/", status_code=status.HTTP_200_OK)
async def read_users_me_allerts(current_user: User = Depends(get_current_user)):
    """API call to get the curret users allerts

    Args:
        current_user (User, optional): User. Defaults to Depends(get_current_user).

    Returns:
        str[]: List of allerts
    """
    return await get_user_allerts(current_user)

@router.get("/users/all/", response_model=List[User])
async def read_users(current_user: User = Depends(get_current_user)):
    """_summary_

    Args:
        current_user (User, optional): _description_. Defaults to Depends(get_current_user).

    Returns:
        _type_: _description_
    """
    await is_admin(current_user)
    return get_all_users(current_user.organization.id)

@router.post("/users/login/", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """API call to create an access token

    Args:
        form_data (OAuth2PasswordRequestForm, optional): Login data. Defaults to Depends().

    Raises:
        HTTPException: Raises error if the email or password or incorrect

    Returns:
        dict: Token information in json format
    """

    #note: username is the reserved name for the login name, must be used even if we are using email
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/users/signup/", status_code=status.HTTP_201_CREATED)
async def register( email: str = Form(),
                    password: str = Form(),
                    first_name: str = Form(),
                    last_name: str = Form(),
                    organization: str = Form()):
    """API call to create a new account

    Args:
        email (str, optional): Email. Defaults to Form().
        password (str, optional): Plaintext password. Defaults to Form().
        first_name (str, optional): Frist name. Defaults to Form().
        last_name (str, optional): Last name Defaults to Form().

    Raises:
        HTTPException: _description_
        HTTPException: _description_

    Returns:
        _type_: _description_
    """
    errors = []
    errors.extend(validate_email(email))
    errors.extend(validate_password(password))
    errors.extend(validate_first_name(first_name))
    errors.extend(validate_last_name(last_name))
    errors.extend(validate_organization(organization))
    if len(errors) > 0:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail=errors,
        )
    if get_user(email):
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="This email is already assosiated with an existing account",
        )

    organization_obj = organizations_table.get_orga(organization)
    if organization_obj is None:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Organization doesnt exist.",
        )

    hashed_pw = get_password_hash(password)
    user = UserWithSensitiveInfo(   email=email,
                                    first_name=first_name,
                                    last_name=last_name,
                                    hashed_password=hashed_pw,
                                    organization= organization_obj,
                                    permission=1,
                                    disabled=0,
                                    email_verified=0)

    if users_table.create_user(user):
        return {"message": "success"}

    return {"message": "couldnt create user."}


@router.post("/users/me/update", status_code=status.HTTP_200_OK)
async def update_user_info(current_user: User = Depends(get_current_user),
                           email: str | None = None, password: str | None = None,
                           first_name: str | None = None, last_name: str | None = None)-> bool:
    """API call to update the current user

    Args:
        current_user (User, optional): _description_. Defaults to Depends(get_current_user).
        email (str | None, optional): new email. Defaults to None.
        password (str | None, optional): password. Defaults to None.
        first_name (str | None, optional): new first name. Defaults to None.
        last_name (str | None, optional): new last name. Defaults to None.

    Returns:
        bool: _description_
    """

    success = await update_user_func(current_user,email,password,first_name,last_name)

    return success

@router.post("/users/update", status_code=status.HTTP_200_OK)
async def admin_update_user_info(
                                update_user_id: int,
                                current_user: User = Depends(get_current_user),
                                email: str | None = None, password: str | None = None,
                                first_name: str | None = None, last_name: str | None = None,
                                organization_name: str | None = None, permission: int | None=None,
                                disabled: bool |None=None, email_verified:bool|None=None) -> bool:
    """API call to update the selected user.

    Args:
        update_user_email (str): _description_
        current_user (User, optional): _description_. Defaults to Depends(get_current_user).
        email (str | None, optional): _description_. Defaults to None.
        password (str | None, optional): _description_. Defaults to None.
        first_name (str | None, optional): _description_. Defaults to None.
        last_name (str | None, optional): _description_. Defaults to None.
        organization_name (str | None, optional): _description_. Defaults to None.
        permission (int | None, optional): _description_. Defaults to None.
        disabled (bool | None, optional): _description_. Defaults to None.
        email_verified (bool | None, optional): _description_. Defaults to None.

    Raises:
        HTTPException: if you dont have the permission to do this (youre not an admin).
        HTTPException: if youre not part of the orga, the user is part of.

    Returns:
        bool: if the update was successful.
    """
    await is_admin(current_user)
    user_to_update = get_user_by_id(update_user_id)

    #check if the user is in the organization of the admin.
    if user_to_update.organization.id != current_user.organization.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You dont have the permission to do this (Not part of the orga).",
        )

    updated_user = await update_user_func(user_to_update,
                               email,
                               password,
                               first_name,
                               last_name,
                               organization_name,
                               permission,
                               disabled,
                               email_verified)

    return updated_user
