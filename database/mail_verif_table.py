import sqlite3
from classes import Token, User
from database.database import database_connection

MAIL_VERIFY_TABLE = """ CREATE TABLE IF NOT EXISTS mail_verification (
                        id integer PRIMARY KEY,
                        email text NOT NULL UNIQUE,
                        token text NOT NULL,
                    ); """

INSERT_TOKEN = 'INSERT INTO mail_verification (email,token) VALUES (? ,? );'


def store_token(user:User, token:Token):
    """Create an entry for an user.

    Args:
        conn (sqlite3.Connection): Connection to a sqlite database.
        email (str): email adress of the user.
        pass_hash (str): hash of the entered password.
    """
    try:
        with database_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(INSERT_TOKEN,(user.email, token.access_token))
            conn.commit()
            cursor.close()
    except sqlite3.IntegrityError:
        print('user with this email already exists.')
