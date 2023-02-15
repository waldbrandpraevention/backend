"""funcs to read and write on the users table in database."""
from enum import Enum
from typing import List

from api.dependencies.classes import User, UserWithSensitiveInfo, Permission
from database.database import fetched_match_class
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
    """Enum class containing all possible user attributes."""
    EMAIL = 'email'
    FIRST_NAME = 'first_name'
    LAST_NAME = 'last_name'
    PASSWORD = 'password'
    PERMISSION = 'permission'
    DISABLED = 'disabled'
    EMAIL_VERIFIED = 'email_verified'
    ORGA_ID = 'organization_id'

UPDATE_ATTRIBUTE = 'UPDATE users SET {} = ? WHERE id = ?;'
UPDATE_STR = 'UPDATE users SET {} WHERE id = ?;'

DELETE = "DELETE from users WHERE id = ?"

INSERT_USER = """INSERT INTO users
                (email,first_name,last_name,organization_id,password,permission,disabled,email_verified) 
                VALUES (? ,? ,?,?,?,?,?,?);"""
GET_USER_WITH_ORGA = '''SELECT
                        users.id,
                        email,
                        first_name,
                        last_name,
                        password,
                        permission,
                        disabled,
                        email_verified,
                        orga.id,
                        orga.name,
                        orga.abbreviation
                        FROM users 
                        JOIN organizations orga ON orga.id = organization_id 
                        WHERE {}=?;'''
CHECK_CREDS = "SELECT password FROM users WHERE EMAIL=? AND PASSWORD = ?;"

def create_user(user:UserWithSensitiveInfo) -> bool:
    """Create an entry for an user.

    Args:
        conn (sqlite3.Connection): Connection to a sqlite database.
        email (str): email adress of the user.
        pass_hash (str): hash of the entered password.
    """
    inserted_id = db.insert(INSERT_USER,
                            (user.email,
                             user.first_name,
                             user.last_name,
                             user.organization.id,
                             user.hashed_password,
                             user.permission.value,
                             user.disabled,
                             user.email_verified))
    if inserted_id:
        user.id = inserted_id
        return True
    return False

def get_user(email, with_sensitive_info:bool=True) -> UserWithSensitiveInfo | None:
    """Get the user object by email.

    Args:
        email (str): email adress of the user.

    Returns:
        user: User object or None.
    """
    sql = GET_USER_WITH_ORGA.format(UsrAttributes.EMAIL)
    fetched_user = db.fetch_one(sql,(email,))
    try:
        user = get_obj_from_fetched(fetched_user,with_sensitive_info)
    except ValueError as exception:
        print(exception)
        user = None
    return user

def get_user_by_id(user_id:int, with_sensitive_info:bool=False) -> UserWithSensitiveInfo | None:
    """Get the user object by email.

    Args:
        email (str): email adress of the user.

    Returns:
        user: User object or None.
    """
    sql = GET_USER_WITH_ORGA.format('users.id')
    fetched_user = db.fetch_one(sql,(user_id,))
    try:
        user = get_obj_from_fetched(fetched_user,with_sensitive_info)
    except ValueError as exception:
        print(exception)
        user = None
    return user

def get_all_users(orga_id:int)-> List[User]:
    """fetches all user in this orga.

    Args:
        orga_id (int): id of the organization.

    Returns:
        List[User]: list of users of this orga.
    """
    sql = GET_USER_WITH_ORGA.format(UsrAttributes.ORGA_ID)
    fetched_users = db.fetch_all(sql,(orga_id,))
    if fetched_users is None:
        return None
    output = []
    for fetched in fetched_users:
        try:
            user = get_obj_from_fetched(fetched,False)
            output.append(user)
        except ValueError as exception:
            print(exception)

    return output

def update_user(user_id:int, attribute:UsrAttributes, new_value):
    """update an attribute of an user.

    Args:
        user_id (int): id of the user.
        attribute (UsrAttributes): attribute that should be updated.
        new_value (_type_): the new value of the choosen attribute.
    """
    update_str = UPDATE_ATTRIBUTE.format(attribute)
    return db.update(update_str,(new_value, user_id))

def delete_user(user_id:int)->bool:
    """remove user from db.

    Args:
        user_id (int): user to delete.

    Returns:
        bool: True if removal was successful.
    """
    return db.update(DELETE,(user_id,))

def update_user_withsql(user_id:int, col_str: str, update_arr:List):
    """updates the user with the given sql str.

    Args:
        user_id (int): _description_
        set_sql (str): _description_

    Returns:
        bool: if the update was successful.
    """
    update_str = UPDATE_STR.format(col_str)
    update_arr.append(user_id)
    update_tuple = tuple(update_arr)
    return db.update(update_str,update_tuple)


def check_creds(mail:str,hashed_pass:str) -> bool:
    """user to check the creds for.

    Args:
        mail (str): mail of the user.
        hashed_pass (str): hashed pw of the

    Returns:
        bool: True if creds match, False if not.
    """
    return db.check_fetch(CHECK_CREDS, (mail, hashed_pass))


def get_obj_from_fetched(fetched_user,
                         with_sensitive_info:bool
                         ) -> User | UserWithSensitiveInfo | None:
    """generate User obj from fetched element.

    Args:
        fetched_user (list): fetched attributes from User.

    Returns:
        UserWithSensitiveInfo | None: User object or None if obj cant be generated.
    """

    if not fetched_match_class(UserWithSensitiveInfo,fetched_user, add=2):
        raise ValueError('Fetched data noch matching format.')

    try:
        permission = Permission(fetched_user[5])
    except ValueError:
        permission = None
    try:
        orga = organizations.get_obj_from_fetched(fetched_user[-3:])
    except IndexError:
        orga = None

    if with_sensitive_info:
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
    else:
        user = User(
                    id=fetched_user[0],
                    email=fetched_user[1],
                    first_name=fetched_user[2],
                    last_name=fetched_user[3],
                    permission=permission,
                    disabled=fetched_user[6],
                    email_verified=fetched_user[7],
                    organization=orga)

    return user
