"""DB functions for user settings"""
from enum import Enum
import json

from api.dependencies.classes import UserSetting, SettingsType
from database.database import fetched_match_class
import database.database as db
from database import settings_table

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

GET_DEFAULTUSERSETTING = '''    SELECT settings_id, user_id, settings.name, settings.description, settings.default_val, settings.type
                                FROM user_settings
                                JOIN settings ON settings.id = settings_id 
                                WHERE settings_id=?;'''
#id           integer NOT NULL ,
# name         text NOT NULL ,
# description text NOT NULL ,
# default_val integer NOT NULL,

class UsrsettingsAttributes(str,Enum):
    """User settings class"""
    SETTING_NAME = 'key'
    SETTING_VALUE = 'value'
    USER_ID = 'user_id'
    SETTING_ID = 'user_id'


def set_usersetting(setting_id:int, user_id:int, value:str)-> bool:
    """Create a setting entry for an user.

    Args:
        setting_id (int): id of the setting(settings_table).
        user_id (int): id of the user.
        value (str): value converted to a str.

    Returns:
        bool: wether the setting could be stored or not.
    """
    inserted_id=db.insert(SET_USERSETTING,(setting_id, user_id, value))
    if inserted_id:
        return True
    return False

def get_usersetting(setting_id:int, user_id:int) -> UserSetting:
    """get a setting, set for a user.

    Args:
        setting_id (int): id of the setting(settings_table).
        user_id (int): id of the user.

    Returns:
        UserSetting: Usersetting obj, standardvalue if not set.
    """
    fetched_setting = db.fetch_one(GET_USERSETTING,(setting_id, user_id))
    user_setting_obj = get_obj_from_fetched(fetched_setting)
    #if not setting set, use the default value.
    if not user_setting_obj:
        setting_obj = settings_table.get_setting(setting_id)
        value = get_value(setting_obj.default_value,setting_obj.type)
        user_setting_obj= UserSetting(
            id = setting_id,
            user_id=user_id,
            name=setting_obj.name,
            description=setting_obj.description,
            value=value,
            type=setting_obj.type
        )
    return user_setting_obj


def get_obj_from_fetched(fetched_setting) -> UserSetting:
    """generate Setting obj from fetched element.

    Args:
        fetched_setting (list): fetched attributes from setting.

    Returns:
        Setting: setting object.
    """
    if fetched_match_class(UserSetting,fetched_setting):

        settings_type = fetched_setting[5]
        value = get_value(fetched_setting[4],settings_type)

        setting_obj = UserSetting(
            id=fetched_setting[0],
            user_id=fetched_setting[1],
            name=fetched_setting[2],
            description=fetched_setting[3],
            value=value,
            type=settings_type
        )
        return setting_obj
    return None

def get_value(value,settings_type) -> int|str|dict:
    """convert stored text value into the given type.

    Args:
        value (_type_): stored value.
        type (int): stored type.

    Returns:
        int|str|dict: converted value.
    """
    if settings_type == SettingsType.INTEGER:
        type_value=int(value)
    elif settings_type == SettingsType.STRING:
        type_value=str(value)
    elif settings_type == SettingsType.JSON:
        type_value=json.loads(value)
    else:
        type_value = None

    return type_value
