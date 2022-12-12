import sqlite3

from api.dependencies.classes import User, UserWithSensitiveInfo, Permission
from database.database import database_connection

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

UPDATE_MAIL = ''' UPDATE users
                    SET email = ? ,
                    WHERE email = ?;'''

UPDATE_PWHASH = ''' UPDATE users
                    SET password = ? ,
                    WHERE email = ?;'''

INSERT_USER = 'INSERT INTO users (email,first_name,last_name,organization_id,password,permission,disabled,email_verified) VALUES (? ,? ,?,?,?,?,?,?);'
GET_USER = 'SELECT * FROM users WHERE EMAIL=?;'
CHECK_CREDS = "SELECT password FROM users WHERE EMAIL=? AND PASSWORD = ?;"

def create_user(user:UserWithSensitiveInfo):
    """Create an entry for an user.

    Args:
        conn (sqlite3.Connection): Connection to a sqlite database.
        email (str): email adress of the user.
        pass_hash (str): hash of the entered password.
    """
    try:
        with database_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(INSERT_USER,(user.email, user.first_name,user.last_name,user.organization,user.hashed_password,user.permission.value,user.disabled,user.email_verified))
            conn.commit()
            cursor.close()
    except sqlite3.IntegrityError as e:##TODO create Email exists exception and raise it here
        print(e)

def get_user(email) -> UserWithSensitiveInfo | None:
    """Get the user object by email.

    Args:
        email (str): email adress of the user.

    Returns:
        user: User object or None.
    """
    try:
        with database_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(GET_USER,(email,))
            fetched_user = cursor.fetchone()
            if not fetched_user:  # An empty result evaluates to False.
                cursor.close()
                return None
            else:
                try:
                    permission = Permission(fetched_user[6])
                    user = UserWithSensitiveInfo(email=fetched_user[1],
                                            first_name=fetched_user[2],
                                            last_name=fetched_user[3],
                                            organization=fetched_user[4],
                                            hashed_password=fetched_user[5],
                                            permission=permission,
                                            disabled=fetched_user[7],
                                            email_verified=fetched_user[8])
                except:
                    user = None
                cursor.close()
                return user
    except Exception as e:
        print(e)
    

def update_mail(user:User | UserWithSensitiveInfo, new_email):
    """Update the email address of a user.

    Args:
        new_email (str): new email adress of the user.
    """
    try:
        with database_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(UPDATE_MAIL,(user.email, new_email))
            conn.commit()
            cursor.close()
            user.email = new_email
    except sqlite3.IntegrityError:
        print('There is already an account with this email.')

def update_password_hash(user:UserWithSensitiveInfo, new_pwhash):
    """Update the password of a user.

    Args:
        new_pwhash (str): new password hash.
    """
    try:
        with database_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(UPDATE_PWHASH,(new_pwhash, user.email))
            conn.commit()
            cursor.close()
            user.hashed_password = new_pwhash
    except sqlite3.Error as e:
        print(e)


def check_creds(user:UserWithSensitiveInfo) -> bool:
    """user to check the creds for.

    Args:
        user (UserWithSensitiveInfo): User object that should be checked.

    Returns:
        bool: True if creds match, False if not.
    """
    with database_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CHECK_CREDS, (user.email, user.hashed_password))
        if not cursor.fetchone():  # An empty result evaluates to False.
            cursor.close()
            return False
        else:
            cursor.close()
            return True