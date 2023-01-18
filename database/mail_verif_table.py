import sqlite3
import database.database as db

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
        db.insert(INSERT_TOKEN,(mail, token))
    except sqlite3.IntegrityError:
        db.update(UPDATE_TOKEN,(token,mail))


def check_token(token:str) -> bool:
    """Checks if token exists in the Database

    Args:
        token (str): the token sent by mail.

    Returns:
        bool: Wether the token exists or not.
    """
    return db.check_fetch(CHECK_TOKEN, (token,))

def get_mail_by_token(token:str) -> str | None:
    """get the mail associated with this token.

    Args:
        token (str): access token.

    Returns:
        str: the email or None if the token wasnt found in the database.
    """
    fetched_mail = db.fetch_one(GET_MAIL_BY_TOKEN,(token,))
    if fetched_mail:
        return fetched_mail[0]
    return None


def get_token_by_mail(mail:str) -> str | None:
    """get the token associated with this mail.

    Args:
        mail (str): mail adress of the user.

    Returns:
        str: the token or None if the mail wasnt found in the database.
    """
    fetched_token = db.fetch_one(GET_TOKEN_BY_MAIL,(mail,))
    if fetched_token:
        return fetched_token[0]
    return None

