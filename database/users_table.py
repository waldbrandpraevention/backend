from enum import Enum
import sqlite3

from api.dependencies.classes import User, UserWithSensitiveInfo, Permission
from database.database import database_connection, fetched_match_class
import database.database as db
from database import organizations_table as organizations

CREATE_USER_TABLE = """ CREATE TABLE IF NOT EXISTS users (
                        id INTEGER,
                        email TEXT NOT NULL UNIQUE,
                        first_name TEXT NOT NULL,
                        last_name TEXT NOT NULL,
                        password TEXT NOT NULL,
                        permission INTEGER DEFAULT 1,
                        disabled INTEGER DEFAULT 0,
                        email_verified INTEGER NOT NULL,
                        organization_id integer NOT NULL,

                        PRIMARY KEY (id),
                        FOREIGN KEY (organization_id) REFERENCES organizations (id)
                    );
                    CREATE UNIQUE INDEX IF NOT EXISTS users_AK ON users (email);
                    CREATE INDEX IF NOT EXISTS users_FK_1 ON users (organization_id);"""

class UsrAttributes(str,Enum):
    EMAIL = 'email'
    FIRST_NAME = 'first_name'
    LAST_NAME = 'last_name'
    PASSWORD = 'password'
    PERMISSION = 'permission'
    DISABLED = 'disabled'
    EMAIL_VERIFIED = 'email_verified'
    ORGA_ID = 'organization_id'

UPDATE_ATTRIBUTE = 'UPDATE users SET {} = ? WHERE id = ?;'

INSERT_USER = 'INSERT INTO users (email,first_name,last_name,organization_id,password,permission,disabled,email_verified) VALUES (? ,? ,?,?,?,?,?,?);'
GET_USER_WITH_ORGA = '''SELECT users.id,email,first_name,last_name,password,permission,disabled,email_verified,orga.id,orga.name,orga.abbreviation
                        FROM users 
                        JOIN organizations orga ON orga.id = organization_id 
                        WHERE EMAIL=?;'''
CHECK_CREDS = "SELECT password FROM users WHERE EMAIL=? AND PASSWORD = ?;"

def create_user(user:UserWithSensitiveInfo) -> bool:
    """Create an entry for an user.

    Args:
        conn (sqlite3.Connection): Connection to a sqlite database.
        email (str): email adress of the user.
        pass_hash (str): hash of the entered password.
    """
    inserted_id = db.insert(INSERT_USER,(user.email, user.first_name,user.last_name,user.organization.id,user.hashed_password,user.permission.value,user.disabled,user.email_verified))
    if inserted_id:
        user.id = inserted_id
        return True
    return False

def get_user(email) -> UserWithSensitiveInfo | None:
    """Get the user object by email.

    Args:
        email (str): email adress of the user.

    Returns:
        user: User object or None.
    """
    fetched_user = db.fetch_one(GET_USER_WITH_ORGA,(email,))
    try:
        user = get_obj_from_fetched(fetched_user)
    except Exception as e:
        print(e)
        user = None
    return user

def update_user(user_id:int, attribute:UsrAttributes, new_value):
    """update an attribute of an user.

    Args:
        user_id (int): id of the user.
        attribute (UsrAttributes): attribute that should be updated.
        new_value (_type_): the new value of the choosen attribute.
    """
    update_str = UPDATE_ATTRIBUTE.format(attribute)
    return db.update(update_str,(new_value, user_id))


def check_creds(mail:str,hashed_pass:str) -> bool:
    """user to check the creds for.

    Args:
        mail (str): mail of the user.
        hashed_pass (str): hashed pw of the

    Returns:
        bool: True if creds match, False if not.
    """
    return db.check_fetch(CHECK_CREDS, (mail, hashed_pass))


def get_obj_from_fetched(fetched_user) -> UserWithSensitiveInfo | None:
    """generate User obj from fetched element.

    Args:
        fetched_user (list): fetched attributes from User.

    Returns:
        UserWithSensitiveInfo | None: User object or None if obj cant be generated.
    """

    if not fetched_match_class(UserWithSensitiveInfo,fetched_user, add=2):
        raise Exception('Fetched data noch matching format.')

    try:
        permission = Permission(fetched_user[5])
    except:
        permission = None
    try:
        orga = organizations.get_obj_from_fetched(fetched_user[-3:])
    except:
        orga = None
    
    user = UserWithSensitiveInfo(
                            id=fetched_user[0],
                            email=fetched_user[1],
                            first_name=fetched_user[2],
                            last_name=fetched_user[3],
                            hashed_password=fetched_user[4],
                            permission=permission,
                            disabled=fetched_user[6],
                            email_verified=fetched_user[7],
                            organization=orga)
    
    return user