from enum import Enum
import sqlite3

from api.dependencies.classes import User, UserWithSensitiveInfo
from database.database import database_connection


CREATE_USERSETTINGS_TABLE = '''
CREATE TABLE user_settings
(
settings_id integer NOT NULL ,
user_id     integer NOT NULL ,
value       integer NOT NULL ,
PRIMARY KEY (settings_id, user_id),
FOREIGN KEY (user_id) REFERENCES users (id),
FOREIGN KEY (settings_id) REFERENCES settings (id)
);

CREATE INDEX user_settings_FK_2 ON user_settings (user_id);
CREATE INDEX user_settings_FK_3 ON user_settings (settings_id);'''

SET_USERSETTING = 'INSERT OR REPLACE INTO user_settings (settings_id,user_id,value) VALUES (? ,? ,?);'
GET_USERSETTING = 'SELECT value FROM user_settings WHERE settings_id=? AND user_id=?;'

class UsrsettingsAttributes(str,Enum):
    SETTING_NAME = 'key'
    SETTING_VALUE = 'value'
    USER_ID = 'user_id'
    SETTING_ID = 'user_id'


def set_usersetting(setting_id:int, user_id:int, value:int):
    """Create a setting entry for an user.

    Args:
        user (UserWithSensitiveInfo | User): _description_
        setting (_type_): _description_
        newvalue (_type_): _description_
    """
    try:
        with database_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(SET_USERSETTING,(setting_id, user_id, value))
            conn.commit()
            cursor.close()
    except sqlite3.IntegrityError as e:##TODO
        print(e)

def get_usersetting(setting_id:int, user_id:int) -> int|None:
    """_summary_

    Args:
        setting_id (int): _description_
        user_id (int): _description_

    Returns:
        int|None: _description_
    """
    try:
        with database_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(GET_USERSETTING,(setting_id, user_id))
            fetched_usersetting = cursor.fetchone()
            cursor.close()
            if fetched_usersetting:
                return fetched_usersetting[0]
    except sqlite3.IntegrityError as e:##TODO
        print(e)
    
    return None

