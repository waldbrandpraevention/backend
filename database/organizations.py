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


def create_orga(organame, orgaabb):
    """Create an entry for an orga.

    Args:
        conn (sqlite3.Connection): Connection to a sqlite database.
    """
    try:
        with database_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(INSERT_ORGA,(organame,orgaabb))
            conn.commit()
            cursor.close()
    except sqlite3.IntegrityError:##TODO create name exists exception and raise it here
        print('organization with this name already exists.')
