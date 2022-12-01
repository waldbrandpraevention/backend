import sqlite3
import configparser
from typing import Union

CREATE_USER_TABLE = """ CREATE TABLE IF NOT EXISTS users (
                        id integer PRIMARY KEY,
                        email text NOT NULL UNIQUE,
                        password text NOT NULL,
                    ); """

UPDATE_MAIL = ''' UPDATE users
                    SET email = ? ,
                    WHERE email = ?;'''

UPDATE_PWHASH = ''' UPDATE users
                    SET password = ? ,
                    WHERE email = ?;'''

INSERT_USER = 'INSERT INTO users (email,password) VALUES (? ,? );'
CHECK_CREDS = "SELECT password FROM users WHERE EMAIL=? AND PASSWORD = ?;"

CONFIG_PATH='config.ini'
config = configparser.ConfigParser(CONFIG_PATH)

DATABASE_PATH = config.get('Database','path')
BACKUP_PATH = config.get('Database','backuppath')

active_connections = []

EMAIL_REGEX = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"

def create_backup():
    """Creates a backup in the path specified in the config.ini.
    """
    database_conn = connect()
    backup_conn = connect(BACKUP_PATH)

    database_conn.backup(backup_conn)

    close_connection(backup_conn)
    close_connection(database_conn)

def connect(path=DATABASE_PATH) -> Union[sqlite3.Connection,None]:
    """creates a connection to the database specified in the congig.ini.

    Returns:
        sqlite3.Connection: Connection to the sqlite database or None.
    """
    #threading mode     threadsafety attribute
    #single-thread 	    0
    #multi-thread 	    1
    #serialized 	    3
    if sqlite3.threadsafety == 3:
        check_same_thread = False
    else:
        check_same_thread = True

    conn = None
    try:
        conn = sqlite3.connect(path, check_same_thread=check_same_thread)
        active_connections.append(conn)
        return conn
    except Exception as e:
        print(e)

    return conn

def close_connection(conn:sqlite3.Connection)->None:
    """closes active sqlite3 connection.

    Args:
        conn (sqlite3.Connection): Connection to a sqlite database.
    """
    try:
        conn.close()
        try:
            active_connections.remove(conn)
        except ValueError as e: #conn 
            print(e)

    except sqlite3.Error as e:
        print(e)


def create_table(conn:sqlite3.Connection, create_table_sql:str)-> None:
    """create a table from the create_table_sql statement

    Args:
        conn (sqlite3.Connection): Connection object
        create_table_sql (str): a CREATE TABLE statement
    """
    try:
        cursor = conn.cursor()
        cursor.execute(create_table_sql)
        conn.commit()
        cursor.close()
    except sqlite3.Error as e:
        print(e)


def create_user(conn:sqlite3.Connection, email, pwhash):
    """Create an entry for an user.

    Args:
        conn (sqlite3.Connection): Connection to a sqlite database.
        email (str): email adress of the user.
        pass_hash (str): hash of the entered password.
    """
    try:
        cursor = conn.cursor()
        cursor.execute(INSERT_USER,(email, pwhash))
        conn.commit()
        cursor.close()
    except sqlite3.IntegrityError:
        print('user with this email already exists.')

def update_mail(conn:sqlite3.Connection, old_email, new_email):
    """Update the users email address.

    Args:
        conn (sqlite3.Connection): Connection to a sqlite database.
        old_email (str): current email adress of the user.
        new_email (str): new email adress of the user.
    """
    try:
        cursor = conn.cursor()
        cursor.execute(UPDATE_MAIL,(old_email, new_email))
        conn.commit()
        cursor.close()
    except sqlite3.IntegrityError:
        print('There is already an account with this email.')

def update_pwhash(conn:sqlite3.Connection, new_pwhash, email):
    """Update the users email address.

    Args:
        conn (sqlite3.Connection): Connection to a sqlite database.
        old_email (str): current email adress of the user.
        new_email (str): new email adress of the user.
    """
    try:
        cursor = conn.cursor()
        cursor.execute(UPDATE_PWHASH,(new_pwhash, email))
        conn.commit()
        cursor.close()
    except sqlite3.Error as e:
        print(e)


def check_creds(conn:sqlite3.Connection, email:str, pwhash:str) -> bool:
    """Check if the given email and hash matches with the ones stored in the database.

    Args:
        conn (sqlite3.Connection): Connection to the sqlite database
        email (str): email adress of the user.
        pass_hash (str): hash of the entered password.

    Returns:
        bool: True if mail and hash match, False if not.
    """
    cursor = conn.cursor()
    cursor.execute(CHECK_CREDS, (email, pwhash))
    if not cursor.fetchone():  # An empty result evaluates to False.
        cursor.close()
        return False
    else:
        cursor.close()
        return True

