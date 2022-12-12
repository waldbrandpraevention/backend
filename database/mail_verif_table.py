import sqlite3
from api.dependencies.classes import User
from database.database import database_connection

CREATE_MAIL_VERIFY_TABLE = """ CREATE TABLE IF NOT EXISTS mail_verification
                                (
                                email text NOT NULL ,
                                token text NOT NULL ,

                                PRIMARY KEY (email)
                                );"""

INSERT_TOKEN = 'INSERT INTO mail_verification (email,token) VALUES (? ,? );'
UPDATE_TOKEN = ''' UPDATE mail_verification SET token = ? WHERE email = ?;'''
CHECK_TOKEN = "SELECT * FROM mail_verification WHERE token=?;"
GET_MAIL_BY_TOKEN = 'SELECT email FROM mail_verification WHERE token=?;'
GET_TOKEN_BY_MAIL = 'SELECT token FROM mail_verification WHERE email=?;'

def store_token(mail:str, token:str):
    """Store the token.

    Args:
        mail (str): mail of the user.
        token (str): token sent to the provided mail.
    """
    try:
        with database_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(INSERT_TOKEN,(mail, token))
            except sqlite3.IntegrityError:
                cursor.execute(UPDATE_TOKEN,(token, mail))
            conn.commit()
            cursor.close()
    except sqlite3.IntegrityError:#TODO check token
        print('there is already a token.')


def check_token(token:str) -> bool:
    """Checks if token exists in the Database

    Args:
        token (str): the token sent by mail.

    Returns:
        bool: Wether the token exists or not.
    """
    with database_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CHECK_TOKEN, (token,))
        if not cursor.fetchone():  # An empty result evaluates to False.
            cursor.close()
            return False
        else:
            cursor.close()
            return True

def get_mail_by_token(token:str) -> str | None:
    """get the mail associated with this token.

    Args:
        token (str): access token.

    Returns:
        str: the email or None if the token wasnt found in the database.
    """
    with database_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(GET_MAIL_BY_TOKEN,(token,))
        fetched_mail = cursor.fetchone()
        cursor.close()
        if not fetched_mail:  # An empty result evaluates to False.
            return None
        else:
            mail = fetched_mail[0]
            return mail


def get_token_by_mail(mail:str) -> str | None:
    """get the token associated with this mail.

    Args:
        mail (str): mail adress of the user.

    Returns:
        str: the token or None if the mail wasnt found in the database.
    """
    with database_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(GET_TOKEN_BY_MAIL,(mail,))
        fetched_token = cursor.fetchone()
        cursor.close()
        if not fetched_token:  # An empty result evaluates to False.
            return None
        else:
            token = fetched_token[0]
            return token

