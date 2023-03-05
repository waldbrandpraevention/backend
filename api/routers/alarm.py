"""Code for email api"""

from datetime import datetime
from fastapi import status, APIRouter, Depends, HTTPException
from database.incidents import create_incident, get_last_incidents
from ..dependencies.users import get_current_user
from ..dependencies.classes import User

router = APIRouter()

@router.post("/alarm/send/", status_code=status.HTTP_200_OK)
async def alarm_team(drone_name: str,
                    location: str,
                    alarm_type: str,
                    notes: str,
                    current_user: User = Depends(get_current_user)):
    """API call to alarm the team

    Args:
        drone_name (str): drone
        location (str): location
        alarm_type (str): type
        notes (str): notes
        current_user (User, optional): user. Defaults to Depends(get_current_user).

    Returns:
        dict: response
    """

    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Invalid user",
        )

    incident = create_incident(drone_name, location, alarm_type, notes, datetime.now())
    if incident is None:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Error while tring to process the incident",
        )
    return {"message:": "success"}


@router.get("/alarm/get-all/", status_code=status.HTTP_200_OK)
async def get_incidents(amount: int, current_user: User = Depends(get_current_user)):
    """API cal te get all incidents

    Args:
        current_user (User, optional): current user. Defaults to Depends(get_current_user).

    Returns:
        Alarm[]: list of alarms
    """

    if amount < 0:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Amount must be >= 0",
        )

    alarms = get_last_incidents(amount)
    return alarms
