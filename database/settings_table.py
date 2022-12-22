from enum import Enum
import sqlite3
from api.dependencies.classes import Setting
from database.database import database_connection, fetched_match_class

#https://stackoverflow.com/a/10228192, if we need settings that cant be stored as integer

CREATE_SETTINGS_TABLE = '''CREATE TABLE IF NOT EXISTS settings
(
id           integer NOT NULL ,
name         text NOT NULL ,
description text NOT NULL ,
default_val integer NOT NULL,
PRIMARY KEY (id)
);
CREATE UNIQUE INDEX IF NOT EXISTS settings_AK ON settings (name);'''

class SettingsAttributes(str,Enum):
    NAME='name'
    DESCRIPTION ='description'
    DEFAULT_VALUE ='default_val'
    
INSERT_SETTING = 'INSERT INTO settings (name, description,default_val) VALUES (?,?,?);'
UPDATE_SETTING = 'UPDATE settings SET {} = ? WHERE name = ?;'

def create_setting(name:str,description:str, defaul_val: int) -> int | None:
    """create a setting.

    Args:
        name (str): name of the setting
        description (str): description of the setting.

    Returns:
        int | None: Id of the inserted entry, None if an error occurs.
    """
    try:
        with database_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(INSERT_SETTING,(name, description,defaul_val))
            inserted_id = cursor.lastrowid
            conn.commit()
            cursor.close()
            return inserted_id
    except sqlite3.IntegrityError as e:##TODO
        print(e)
    return None

def get_settings():
    """fetch all settings.

    Returns:
        list: list of all settings.
    """
    try:
        with database_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM settings')
            fetched_settings = cursor.fetchall()
            cursor.close()
            output = []
            for setting in fetched_settings:
                if fetched_match_class(Setting,setting):
                    setting_obj = Setting(
                        id=setting[0],
                        name=setting[1],
                        description=setting[2],
                        default_value=setting[3]
                    )
                output.append(setting_obj)
            return output
    except sqlite3.IntegrityError as e:##TODO
        print(e)

def update_setting(setting_name:str, attribute:SettingsAttributes, new_value: str|int):
    """Update an attribute of the settings entry.

    Args:
        setting_name (str): name of the setting.
        attribute (SettingsAttributes): attribute that should be updated.
        new_value (str|int): new_value that should be set.
    """
    try:
        with database_connection() as conn:
            cursor = conn.cursor()
            update_str = UPDATE_SETTING.format(attribute)
            cursor.execute(update_str,(new_value, setting_name))
            conn.commit()
            cursor.close()
    except Exception as e:#TODO
        print(e)