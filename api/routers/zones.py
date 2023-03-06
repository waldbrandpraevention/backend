"""Api calls for Zones."""
from fastapi import Depends, APIRouter, HTTPException, status
from  ..dependencies.zones import get_all_zones, get_zone_by_id, get_zone_count
from .users import get_current_user
from ..dependencies.classes import User, Zone
router = APIRouter()


@router.get("/zones/", status_code=status.HTTP_200_OK, response_model=Zone)
async def read_zone(zone_id: int, current_user: User = Depends(get_current_user)):
    """API call to get a specific zone. The zone has to be linked to the current_user's orga.

    Args:
        zone_id (int): id of the zone.
        current_user (User): User. Defaults to User that is logged in.

    Returns:
        Zone: zone
    """

    zone = await get_zone_by_id(zone_id, current_user.organization.id)
    if not zone:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Zone does not exist or isnt linked to your orga.",
        )
    return zone

@router.get("/zones/all/", status_code=status.HTTP_200_OK, response_model=list[Zone])
async def read_zones_all(current_user: User = Depends(get_current_user)):
    """API call to get the all zones, linked with current_user's orga.

    Args:
        current_user (User): User. Defaults to User that is logged in.

    Returns:
        Zone[]: List of Zones.
    """
    zones = await get_all_zones(current_user.organization.id)
    if not zones:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Your Organization has no zones linked to it",
        )
    return zones

@router.get("/zones/count/", status_code=status.HTTP_200_OK, response_model=dict)
async def read_zones_count(current_user: User = Depends(get_current_user)):
    """API call to get the amount of zones, linked with current_user's orga.

    Args:
        current_user (User): User. Defaults to User that is logged in.

    Returns:
        int: amount of zones.
    """

    return {"count": await get_zone_count(current_user.organization.id)}
