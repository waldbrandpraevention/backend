""" API routes for territories."""
from typing import List
from fastapi import Depends, APIRouter, HTTPException, status

from api.dependencies.territories import get_territories, get_territory_by_id
from .users import get_current_user
from ..dependencies.classes import Territory, User
router = APIRouter()


@router.get("/territories/all/", status_code=status.HTTP_200_OK, response_model=List[Territory])
async def read_territories(current_user: User = Depends(get_current_user)):
    """API call to get the all territories, linked with this users orga.

    Args:
        current_user (User, optional): _description_. Defaults to Depends(get_current_user).

    Raises:
        HTTPException: _description_

    Returns:
        _type_: _description_
    """

    zone = await get_territories(current_user.organization.id)
    if not zone:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Your Organization has no territories linked to it",
        )
    return zone

@router.get("/territories/", status_code=status.HTTP_200_OK, response_model=Territory)
async def read_territory(territory_id: int, current_user: User = Depends(get_current_user)):
    """API call to get a specific territory. The user's orga has to be linked to the territory.

    Args:
        name (str): Name of the territory
        current_user (User, optional): User. Defaults to Depends(get_current_user).

    Returns:
        Territory: territory
    """

    territory = await get_territory_by_id(territory_id, current_user.organization.id)
    if territory is None:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Territory does not exist or isnt linked to your orga.",
        )
    return territory
