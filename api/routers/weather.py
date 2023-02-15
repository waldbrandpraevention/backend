from fastapi import APIRouter, Depends, HTTPException, status
from .users import get_current_user
from ..dependencies.classes import User
from ..dependencies.weather import (
    get_current_wind
    )

router = APIRouter()

@router.get("/weather/wind/", status_code=status.HTTP_200_OK)
async def read_weather(current_user: User = Depends(get_current_user)):
    """API call to get wind.

    Args:
        current_user (User, optional): User. Defaults to Depends(get_current_user).

    Returns:
        WindInfo[]: List of WindInfo.
    """
    return get_current_wind()