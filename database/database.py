import os
import sqlite3
import configparser
from contextlib import contextmanager
from typing import List
from pydantic import BaseModel


CONFIG_PATH='config.ini'
config = configparser.ConfigParser()
config.read(CONFIG_PATH)

DATABASE_PATH = config.get('database','path')
BACKUP_PATH = config.get('database','backuppath')

EMAIL_REGEX = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"

file_path = os.path.realpath(__file__)
file_path= os.path.dirname(file_path)
file_path= os.path.dirname(file_path)
spatialite_path = 'mod_spatialite-5.0.1-win-amd64'
spatialite_path = os.path.join(file_path,spatialite_path)
# e.g. spatialite_path  = 'C:/Users/pedro/Documents/mod_spatialite-NG-win-amd64
os.environ['PATH'] = spatialite_path + ';' + os.environ['PATH']

conections = []

def create_backup():
    """Creates a backup in the path specified in the config.ini.
    """
    with database_connection() as database_conn:
        with database_connection(BACKUP_PATH) as backup_conn:
            database_conn.backup(backup_conn)


@contextmanager
def database_connection(path=DATABASE_PATH):
    """returns a db connection, can be used like this:\n
    with database_connection() as conn:
        do stuff here

    Args:
        path (str, optional): path to db. Defaults to DATABASE_PATH.

    Yields:
        sqlite3.Connection: connection to the db.
    """
    conn = connect(path)
    try:
        yield conn
    finally:
        close_connection(conn)
    

def connect(path=DATABASE_PATH) -> sqlite3.Connection | None:
    """creates a connection to the database specified in the congig.ini.

    Returns:
        sqlite3.Connection: Connection to the sqlite database or None.
    """
    #threading mode     threadsafety attribute
    #single-thread 	    0
    #multi-thread 	    1
    #serialized 	    3

    if len(conections)>0:
        return conections.pop()

    if sqlite3.threadsafety == 3:
        check_same_thread = False
    else:
        check_same_thread = True

    conn = None
    try:
        conn = sqlite3.connect(path, check_same_thread=check_same_thread,detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        conn.enable_load_extension(True)
        conn.load_extension("mod_spatialite")
        try:
            conn.execute('SELECT InitSpatialMetaData(1);')
        except:
            pass

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
        if len(conections)>3:
            conn.close()
        else:
            conections.append(conn)

    except sqlite3.Error as e:
        print(e)

def create_table(create_table_sql:str)-> None:
    """create a table from the create_table_sql statement

    Args:
        conn (sqlite3.Connection): Connection object
        create_table_sql (str): a CREATE TABLE statement
    """
    try:
        with database_connection() as conn:
            cursor = conn.cursor()
            cursor.executescript(create_table_sql)
            conn.commit()
            cursor.close()
    except sqlite3.Error as e:
        print(e)

def fetched_match_class(klasse:BaseModel, fetched_object, subtract:int=0) -> bool:
    """checks wether number of fetched attributes matches number of required attributes.

    Args:
        klasse (BaseModel): the class with should be used.
        fetched_object (_type_): the fetched attributes.

    Returns:
        bool: wether the numbers match.
    """
    try:
        if fetched_object:
            if len(klasse.__fields__) - subtract == len(fetched_object):
                return True
    except Exception as e:
        print(e)
    
    return False

def insert(insert_sql:str,insert_tuple=None) -> int | None:
    """inserts into the db.

    Args:
        insert_sql (str): the sql used to insert.
        insert_tuple (tuple): the tuple with the data that should be inserted.

    Returns:
        int | None: the id of the inserted item.
    """
    try:
        with database_connection() as conn:
            cursor = conn.cursor()
            if insert_tuple:
                cursor.execute(insert_sql,insert_tuple)
            else:
                cursor.execute(insert_sql)
            inserted_id = cursor.lastrowid
            conn.commit()
            cursor.close()
            return inserted_id
    except sqlite3.IntegrityError as e:##TODO create Item exists exception and raise it here
        print(e)
        raise e

def update(update_sql:str,update_tuple=None) -> bool:
    """updates an entry in the db.

    Args:
        update_sql (str): the sql used to update.
        update_tuple (tuple): the tuple with the data that should be updated.

    Returns:
        bool: True if update was successful.
    """
    try:
        with database_connection() as conn:
            cursor = conn.cursor()
            if update_tuple:
                cursor.execute(update_sql,update_tuple)
            else:
                cursor.execute(update_sql)
            conn.commit()
            cursor.close()
            return True
    except sqlite3.Error as e:
        print(e)
    return False

def fetch_one(fetch_sql:str,fetch_tuple=None):
    """fetches one result.

    Args:
        fetch_sql (str): sql to get the desired data.
        fetch_tuple (tuple): the tuple with the data that should be fetched.

    Returns:
        List[T]: list with all fetched attributes.
    """
    try:
        with database_connection() as conn:
            cursor = conn.cursor()
            if fetch_tuple:
                cursor.execute(fetch_sql,fetch_tuple)
            else:
                cursor.execute(fetch_sql)
            fetched_user = cursor.fetchone()
            cursor.close()
            return fetched_user
    except Exception as e:
        print(e)
    return None

def fetch_all(fetch_sql:str,fetch_tuple=None):
    """fetches all results.

    Args:
        fetch_sql (str): sql to get the desired data.
        fetch_tuple (tuple): the tuple with the data that should be fetched.

    Returns:
        List[List[T]]: list with all fetched attributes.
    """
    try:
        with database_connection() as conn:
            cursor = conn.cursor()
            if fetch_tuple:
                cursor.execute(fetch_sql,fetch_tuple)
            else:
                cursor.execute(fetch_sql)
            fetched_user = cursor.fetchall()
            cursor.close()
            return fetched_user
    except Exception as e:
        print(e)

    return None

def check_fetch(fetch_sql:str,fetch_tuple=None):
    """checks wrther tuple exists in db.

    Args:
        fetch_sql (str): sql to get the desired data.
        fetch_tuple (tuple): the tuple with the data that should be fetched.

    Returns:
        bool: True if creds match, False if not.
    """
    try:
        with database_connection() as conn:
            cursor = conn.cursor()
            if fetch_tuple:
                cursor.execute(fetch_sql,fetch_tuple)
            else:
                cursor.execute(fetch_sql)
            if not cursor.fetchone():  # An empty result evaluates to False.
                cursor.close()
                return False
            else:
                cursor.close()
                return True
    except Exception as e:
        print(e)
    return False
