from enum import Enum
import sqlite3
from typing import List
from api.dependencies.classes import Setting,SettingsType
from database.database import database_connection, fetched_match_class
import database.database as db


#https://stackoverflow.com/a/10228192, if we need settings that cant be stored as integer

CREATE_SETTINGS_TABLE = '''CREATE TABLE IF NOT EXISTS settings
(
id           integer NOT NULL ,
name         text NOT NULL ,
description text NOT NULL ,
default_val integer NOT NULL,
type        integer NOT NUll,
PRIMARY KEY (id)
);
CREATE UNIQUE INDEX IF NOT EXISTS settings_AK ON settings (name);'''

class SettingsAttributes(str,Enum):
    NAME='name'
    DESCRIPTION ='description'
    DEFAULT_VALUE ='default_val'
    
INSERT_SETTING = 'INSERT INTO settings (name, description,default_val,type) VALUES (?,?,?,?);'
UPDATE_SETTING = 'UPDATE settings SET {} = ? WHERE name = ?;'
GET_SETTING = 'SELECT * FROM settings WHERE ID = ?;'

def create_setting(name:str,description:str, defaul_val: int,type:SettingsType) -> int | None:
    """create a setting.

    Args:
        name (str): name of the setting
        description (str): description of the setting.

    Returns:
        int | None: Id of the inserted entry, None if an error occurs.
    """
    return db.insert(INSERT_SETTING,(name, description,defaul_val,type.value))

def get_settings() -> List[Setting]:
    """fetch all settings.

    Returns:
        list: list of all settings.
    """
    fetched_settings = db.fetch_all('SELECT * FROM settings')
    output = []
    for setting in fetched_settings:
        setting_obj = get_obj_from_fetched(setting)
        if setting_obj:
            output.append(setting_obj)
    return output

def get_setting(setting_id) -> Setting:
    """fetch all settings.

    Returns:
        Setting: setting.
    """
    fetched_settings = db.fetch_one(GET_SETTING,(setting_id,))
    setting_obj = get_obj_from_fetched(fetched_settings)
    return setting_obj

def update_setting(setting_name:str, attribute:SettingsAttributes, new_value: str|int):
    """Update an attribute of the settings entry.

    Args:
        setting_name (str): name of the setting.
        attribute (SettingsAttributes): attribute that should be updated.
        new_value (str|int): new_value that should be set.
    """
    update_str = UPDATE_SETTING.format(attribute)
    db.update(update_str,(new_value, setting_name))

def get_obj_from_fetched(fetched_setting) -> Setting:
    """generate Setting obj from fetched element.

    Args:
        fetched_setting (list): fetched attributes from setting.

    Returns:
        Setting: setting object.
    """
    if fetched_match_class(Setting,fetched_setting):
        setting_obj = Setting(
            id=fetched_setting[0],
            name=fetched_setting[1],
            description=fetched_setting[2],
            default_value=fetched_setting[3],
            type=fetched_setting[4],
        )
        return setting_obj
    return None