"""Code for email api"""

import os
from datetime import datetime
from fastapi import status, APIRouter, UploadFile,File, Depends
from ..dependencies.users import get_current_user
from ..dependencies.classes import User

alarm_location = os.getenv("ALARM_PATH")

router = APIRouter()

@router.post("/alarm/send/", status_code=status.HTTP_200_OK)
async def alarm_team(drone_name: str,
                    location: str,
                    alarm_type: str,
                    notes: str,
                    file: UploadFile | None = File(),
                    current_user: User = Depends(get_current_user)):
    """API call to alarm the team

    Args:
        drone_name (str): drone
        location (str): location
        alarm_type (str): type
        notes (str): notes
        file (UploadFile | None, optional): file Defaults to File().
        current_user (User, optional): user. Defaults to Depends(get_current_user).

    Returns:
        dict: response
    """

    if not current_user:
        return {"message": "Invalid user"}

    try:
        content = f"""
        Drone: {drone_name}
        location: {location}
        type: {alarm_type}
        notes: {notes}
        """
        file_path = os.path.realpath(__file__)
        base_dir_path = os.path.join(file_path,alarm_location,str(datetime.now()))
        dir_path = base_dir_path
        i = 1
        while os.path.exists(dir_path):
            dir_path = base_dir_path + " - " + str(i)
            i = i + 1

        os.makedirs(dir_path)

        with open(f"{dir_path}/info.txt", "wb+") as file_object:
            file_object.write(content)

        file_location = f"{dir_path}/{file.filename}"
        with open(file_location, "wb+") as file_object:
            file_object.write(file.file.read())

        return {"message": "Alarmierung erhalten"}
    except Exception as err:
        print(err)
        return {"message": "Alarmierung fehlgeschlagen"}
