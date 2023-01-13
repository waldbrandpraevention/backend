from enum import Enum
import sqlite3
from typing import List

from api.dependencies.classes import Organization, User, UserWithSensitiveInfo, Permission
from database.database import database_connection, fetched_match_class
import database.database as db

CREATE_ORGANISATIONS_TABLE = """ CREATE TABLE IF NOT EXISTS organizations
                        (
                        id INTEGER, 
                        name         text NOT NULL ,
                        abbreviation text NOT NULL ,

                        PRIMARY KEY (id)
                        );
                        CREATE UNIQUE INDEX IF NOT EXISTS orgs_AK ON organizations (name);"""

INSERT_ORGA =  "INSERT INTO organizations (name,abbreviation) VALUES (?,?);"
GET_ORGA = 'SELECT * FROM organizations WHERE NAME=?;'
GET_ORGA_BY_ID = 'SELECT * FROM organizations WHERE ID=?;'
UPDATE_ORGA_NAME = ''' UPDATE users
                    SET email = ? ,
                    WHERE email = ?;'''
UPDATE_ATTRIBUTE = 'UPDATE organizations SET {} = ? WHERE name = ?;'

class OrgAttributes(str,Enum):
    NAME = 'name'
    ABBREVIATION = 'abbreviation'

def update_orga(orga: Organization, attribute:OrgAttributes, new_value):
    """Update the email address of a user.

    Args:
        new_email (str): new email adress of the user.
    """
    update_str = UPDATE_ATTRIBUTE.format(attribute)
    db.update(update_str,(new_value, orga.name))


def create_orga(organame:str, orga_abb:str):
    """Create an entry for an organization.

    Args:
        organame (str): name of the organization.
        orgaabb (str): abbreviation of the organization.
    """
    db.insert(INSERT_ORGA,(organame,orga_abb))

def get_orga(organame:str) -> Organization | None:
    """get the orga object with this name.

    Args:
        organame (str): orga to look for

    Returns:
        orga: Organization or None.
    """
    fetched_orga = db.fetch_one(GET_ORGA,(organame,))
    return get_obj_from_fetched(fetched_orga)

def get_orga_by_id(orga_id:int) -> Organization | None:
    """get the orga object with this id.

    Args:
        orga_id (int): orga to look for.

    Returns:
        orga: Organization or None.
    """
    fetched_orga = db.fetch_one(GET_ORGA_BY_ID,(orga_id,))
    return get_obj_from_fetched(fetched_orga)

def get_all_orga():
    """Create an entry for an organization.

    Returns:
        List[Organization]: list of all stored organizations.
    """

    fetched_orgas = db.fetch_all('SELECT * FROM organizations')
    output = []
    for orga in fetched_orgas:
        orga_obj = get_obj_from_fetched(orga)
        if orga_obj:
            output.append(orga_obj)
    return output

def get_obj_from_fetched(fetched_orga):
    """generate Organization obj from fetched element.

    Args:
        fetched_orga (list): fetched attributes from orga.

    Returns:
        Organization: orga object.
    """
    if fetched_match_class(Organization,fetched_orga):
        orga_obj = Organization(
            id = fetched_orga[0],
            name=fetched_orga[1],
            abbreviation=fetched_orga[2]
        )
        return orga_obj
    return None