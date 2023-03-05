"""This module contains the incidents table and its related functions."""
from typing import List
import datetime
from database.database import fetched_match_class
import database.database as db
from api.dependencies.classes import Incident

CREATE_INCIDENTS_TABLE = '''CREATE TABLE IF NOT EXISTS incidents
(
id          integer NOT NULL ,
drone_name  text NOT NULL ,
location    text NOT NULL ,
alarm_type  text NOT NULL,
notes       text NOT NULL
timestamp   timestamp NOT NULL
PRIMARY KEY (id)
);'''

INSERT_INCIDENT= 'INSERT INTO incidents (drone_name, location, alarm_type, notes) VALUES (?,?,?,?);'

GET_INCIDENT = '''SELECT id,dr,name,description
                    FROM territories
                    Jo
                    {};'''

GET_TERRITORY_IDS = '''SELECT id
                    FROM territories
                    {};'''


def create_incident(drone_name: str, location: str, alarm_type: str, notes: str, timestamp: datetime.datetime) -> int | None:
    """create an incident.

    Args:
        drone_name (str): name of the drone
        location (str): location of the incident.
        alarm_type (str): alarm_type of the incident.
        notes (str): notes of the incident
        timestamp (datetime): timestamp of the incident

    Returns:
        int | None: Id of the inserted entry, None if an error occurs.
    """
    return db.insert(INSERT_INCIDENT, (drone_name, location, alarm_type, notes, timestamp))

def get_last_incidents(amount: int) -> List[Incident]:
    """returns the last x incidents
    Args:
        amount (int): number of incidents 

    Returns:
        List[Incident]: list of incidents.
    """
    incidents = []

    #todo get last x inicdents by timestamp, if less than x exist -> return as many as exist

    return incidents

def get_obj_from_fetched(fetched_incident: tuple) -> Incident:
    """get a Incident object from a fetched tuple.

    Args:
        fetched_incident (tuple): the fetched tuple.

    Returns:
        Incident: the territory object.
    """
    if fetched_match_class(Incident,fetched_incident,1):
        try:
            incident_obj = Incident(
                id = fetched_incident[0],
                drone_name = fetched_incident[1],
                location = fetched_incident[2],
                alarm_type = fetched_incident[3],
                notes = fetched_incident[4],
                timestamp = fetched_incident[5],
            )
            return incident_obj
        except ValueError as exception:
            print(exception)

    return None
