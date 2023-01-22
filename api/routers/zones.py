from fastapi import Depends, APIRouter, FastAPI, HTTPException, status, Request, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from  ..dependencies.zones import get_all_zones, get_zone, get_zone_count
from .users import get_current_user
from ..dependencies.classes import User, Zone
from database import organizations_table
router = APIRouter()


@router.get("/zones/", status_code=status.HTTP_200_OK, response_model=Zone)
async def read_zone(name: str, current_user: User = Depends(get_current_user)):
    """API call to get a specific zone

    Args:
        name (str): Name of the zone
        current_user (User, optional): User. Defaults to Depends(get_current_user).

    Returns:
        Zone: zone
    """

    zone = await get_zone(name, current_user.organization.id)
    if zone == None:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Zone does not exist ",
        )
    return zone

@router.get("/zones/all/", status_code=status.HTTP_200_OK, response_model=list[Zone])
async def read_zones_all(current_user: User = Depends(get_current_user)):
    """API call to get the all zones

    Args:
        current_user (User, optional): User. Defaults to Depends(get_current_user).

    Returns:
        Zone[]: List of all zones
    """
    return await get_all_zones(current_user.organization.id)

@router.get("/zones/count/", status_code=status.HTTP_200_OK)
async def read_zones_count(current_user: User = Depends(get_current_user)):
    """API call to get the amount of zones
    Args:
        current_user (User, optional): User. Defaults to Depends(get_current_user).

    Returns:
        int: amount of drones
    """

    return {"count": await get_zone_count(current_user.organization.id)}