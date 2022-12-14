from enum import Enum
import sqlite3

from api.dependencies.classes import Organization, User, UserWithSensitiveInfo, Permission
from database.database import database_connection, fetched_match_class

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
    try:
        with database_connection() as conn:
            cursor = conn.cursor()
            update_str = UPDATE_ATTRIBUTE.format(attribute)
            cursor.execute(update_str,(new_value, orga.name))
            conn.commit()
            cursor.close()
    except Exception as e:
        print(e)


def create_orga(organame:str, orga_abb:str):
    """Create an entry for an organization.

    Args:
        organame (str): name of the organization.
        orgaabb (str): abbreviation of the organization.
    """
    try:
        with database_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(INSERT_ORGA,(organame,orga_abb))
            conn.commit()
            inserted_id = cursor.lastrowid
            cursor.close()
            orga = Organization(
                id=inserted_id,
                name=organame,
                abbreviation=orga_abb
            )
            return orga
    except sqlite3.IntegrityError as e:
        print(e)
    return None

def get_orga(organame:str) -> Organization | None:
    """get the orga object with this name.

    Args:
        organame (str): orga to look for

    Returns:
        orga: Organization or None.
    """
    try:
        with database_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(GET_ORGA,(organame,))
            fetched_orga = cursor.fetchone()
            cursor.close()
            if not fetched_orga:  # An empty result evaluates to False.
                return None
            else:
                try:
                    orga =  get_obj_from_fetched(fetched_orga)
                except:
                    orga = None
                
                return orga
    except Exception as e:
        print(e)
    return None


def get_orga_by_id(orga_id:int) -> Organization | None:
    """get the orga object with this id.

    Args:
        orga_id (int): orga to look for.

    Returns:
        orga: Organization or None.
    """
    try:
        with database_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(GET_ORGA_BY_ID,(orga_id,))
            fetched_orga = cursor.fetchone()
            cursor.close()
            if not fetched_orga:  # An empty result evaluates to False.
                return None
            else:
                try:
                    orga =  get_obj_from_fetched(fetched_orga)
                except:
                    orga = None
                
                return orga
    except Exception as e:
        print(e)
    return None

def get_all_orga():
    """Create an entry for an organization.

    Args:
        organame (str): name of the organization.
        orgaabb (str): abbreviation of the organization.
    """
    try:
        with database_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM organizations')
            fetched_orgas = cursor.fetchall()
            cursor.close()
            output = []
            for orga in fetched_orgas:
                orga_obj = get_obj_from_fetched(orga)
                if orga_obj:
                    output.append(orga_obj)
            return output
    except sqlite3.IntegrityError as e:
        print(e)
    return None

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