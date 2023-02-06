"""Tests for the database func"""
import os
import sqlite3
from contextlib import contextmanager
from typing import List
from pydantic import BaseModel

DATABASE_PATH = os.getenv('DB_PATH')
BACKUP_PATH = os.getenv('DB_BACKUP_PATH')

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
    """Creates a backup in the path specified in the env variable.
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
        conn = sqlite3.connect(path,
                               check_same_thread=check_same_thread,
                               detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        conn.enable_load_extension(True)
        if os.name == 'nt':
            conn.load_extension("mod_spatialite") # windows
        else:
            conn.load_extension("mod_spatialite.so.7.1.2") # fix for docker image

    except sqlite3.Error as error:
        print(error)

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

    except sqlite3.Error as exception:
        print(exception)

def initialise_spatialite()-> None:
    """executes the SELECT InitSpatialMetaData(1); sql in order to initialise
        the spatialite tables.
    """
    try:
        with database_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT InitSpatialMetaData(1);')
            conn.commit()
            cursor.close()
    except sqlite3.Error as exception:
        print(exception)

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
    except sqlite3.Error as exception:
        print(exception)

def fetched_match_class(klasse:BaseModel, fetched_object, subtract:int=0,add:int = 0) -> bool:
    """checks wether number of fetched attributes matches number of required attributes.

    Args:
        klasse (BaseModel): the class with should be used.
        fetched_object (_type_): the fetched attributes.

    Returns:
        bool: wether the numbers match.
    """
    if fetched_object:
        if len(klasse.__fields__) - subtract + add == len(fetched_object):
            return True

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
    except sqlite3.IntegrityError as exception:
        raise exception

def insertmany(insert_sql:str,insert_tuple=None) -> int | None:
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
                cursor.executemany(insert_sql,insert_tuple)
            else:
                cursor.executemany(insert_sql)
            rowcount = cursor.rowcount
            conn.commit()
            cursor.close()
            return rowcount
    except sqlite3.IntegrityError as exception:
        print(exception)
        raise exception

def update(update_sql:str,update_tuple=None) -> bool:
    """updates or deletes an entry in the db.

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
    except sqlite3.Error as exception:
        print(exception)
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
    except sqlite3.Error as exception:
        print(exception)
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
            if len(fetched_user)>0:
                return fetched_user
    except sqlite3.Error as exception:
        print(exception)

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
            cursor.close()
            return True
    except sqlite3.Error as exception:
        print(exception)
    return False

def add_where_clause(sql:str, where_param_array:List[str]):
    """concats where_clause and inserts it into sql statement.

    Args:
        sql (_type_): _description_
        where_param_array (List[str]): _description_

    Returns:
        _type_: _description_
    """
    where_clause = ''
    if len(where_param_array)>0:
        witter = iter(where_param_array)
        first_statement = next(witter)

        where_clause = f'WHERE {first_statement}'
        for statement in witter:
            where_clause += f' AND {statement}'

    sql = sql.format(where_clause)
    return sql

def create_where_clause_statement(clmname:str,eqator:str='',questionmark:str='?'):
    """_summary_

    Args:
        clmname (str): _description_
        eqator (str): _description_

    Returns:
        _type_: _description_
    """
    return f'{clmname} {eqator} {questionmark}'

def create_intersection_clause(first_geom:str,second_geom:str='GeomFromGeoJSON(?)'):
    """creates sql that checks for an intersection of the given geoms.

    Args:
        first_geom (str): _description_
        second_geom (str, optional): _description_. Defaults to 'GeomFromGeoJSON(?)'.

    Returns:
        _type_: _description_
    """
    return f'ST_Intersects({first_geom},{second_geom})'
