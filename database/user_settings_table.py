from enum import Enum
import json
import sqlite3

from api.dependencies.classes import User, UserSetting, UserWithSensitiveInfo
from database.database import database_connection, fetched_match_class
import database.database as db
from api.dependencies.classes import SettingsType


CREATE_USERSETTINGS_TABLE = '''
CREATE TABLE user_settings
(
settings_id integer NOT NULL ,
user_id     integer NOT NULL ,
value       text NOT NULL ,
PRIMARY KEY (settings_id, user_id),
FOREIGN KEY (user_id) REFERENCES users (id),
FOREIGN KEY (settings_id) REFERENCES settings (id)
);

CREATE INDEX user_settings_FK_2 ON user_settings (user_id);
CREATE INDEX user_settings_FK_3 ON user_settings (settings_id);'''

SET_USERSETTING = 'INSERT OR REPLACE INTO user_settings (settings_id,user_id,value) VALUES (? ,? ,?);'
GET_USERSETTING = '''   SELECT settings_id, user_id, settings.name, settings.description, value, settings.type
                        FROM user_settings
                        JOIN settings ON settings.id = settings_id 
                        WHERE settings_id=? AND user_id=?;'''
#id           integer NOT NULL ,
# name         text NOT NULL ,
# description text NOT NULL ,
# default_val integer NOT NULL,

class UsrsettingsAttributes(str,Enum):
    SETTING_NAME = 'key'
    SETTING_VALUE = 'value'
    USER_ID = 'user_id'
    SETTING_ID = 'user_id'


def set_usersetting(setting_id:int, user_id:int, value:str):
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
    fetched_setting = db.fetch_one(GET_USERSETTING,(setting_id, user_id))
    return get_obj_from_fetched(fetched_setting)


def get_obj_from_fetched(fetched_setting) -> UserSetting:
    """generate Setting obj from fetched element.

    Args:
        fetched_setting (list): fetched attributes from setting.

    Returns:
        Setting: setting object.
    """
    if fetched_match_class(UserSetting,fetched_setting):
        type = fetched_setting[5]

        if type == SettingsType.INTEGER:
            value=int(fetched_setting[4])
        elif type == SettingsType.STRING:
            value=str(fetched_setting[4])
        elif type == SettingsType.JSON:
            value=json.loads(fetched_setting[4])

        setting_obj = UserSetting(
            id=fetched_setting[0],
            user_id=fetched_setting[1],
            name=fetched_setting[2],
            description=fetched_setting[3],
            value=value,
            type=type
        )
        return setting_obj
    return None

