import sqlite3

from api.dependencies.classes import User, UserWithSensitiveInfo, Permission
from database.database import database_connection

CREATE_ORGANISATIONS_TABLE = """ CREATE TABLE IF NOT EXISTS organizations
                        (
                        name         text NOT NULL ,
                        abbreviation text NOT NULL ,

                        PRIMARY KEY (name)
                        );"""

INSERT_ORGA =  "INSERT INTO organizations (name,abbreviation) VALUES (?,?);"


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
            cursor.close()
    except sqlite3.IntegrityError:##TODO create name exists exception and raise it here
        print('organization with this name already exists.')
