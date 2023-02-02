from fastapi import APIRouter, Depends, HTTPException, status
from ..dependencies.weather import (
    get_current_wind
    )

router = APIRouter()

@router.get("/weather/wind/", status_code=status.HTTP_200_OK, response_model=list[Zone])
async def read_zones_all(current_user: User = Depends(get_current_user)):
    """API call to get wind.

    Args:
        current_user (User, optional): User. Defaults to Depends(get_current_user).

    Returns:
        WindInfo[]: List of WindInfo.
    """
    return get_current_wind()