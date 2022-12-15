from fastapi import Depends, APIRouter, FastAPI, HTTPException, status, Request, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from  ..dependencies.zones import get_all_zones, get_zone
from .users import get_current_user
from ..dependencies.classes import User, Zone

router = APIRouter()


@router.get("/zones/", response_model=User)
async def read_users_me(name: str, current_user: User = Depends(get_current_user)):
    """API call to get a specific zone

    Args:
        name (str): Name of the zone
        current_user (User, optional): User. Defaults to Depends(get_current_user).

    Returns:
        Zone: zone
    """

    zone = get_zone(name)
    if zone == None:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Zone does not exist ",
        )
    return zone

@router.get("/zones/all/", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """API call to get the all zones

    Args:
        current_user (User, optional): User. Defaults to Depends(get_current_user).

    Returns:
        Zone[]: List of all zones
    """
    return get_all_zones()