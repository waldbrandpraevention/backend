"""database tests"""
# setting path
import sqlite3
import asyncio
import datetime
import json
import time
import pytest
from api.routers import zones as api_zones
from api.dependencies.authentication import get_password_hash
from api.dependencies.classes import( Drone,
                                     Organization,
                                     DroneUpdate,
                                     UserWithSensitiveInfo,
                                     SettingsType)
from database.database import create_table
from database.mail_verif_table import (check_token,
                                       get_mail_by_token,
                                       get_token_by_mail,
                                       store_token,
                                       CREATE_MAIL_VERIFY_TABLE
                                       )
from database.users_table import create_user,get_user,UsrAttributes, update_user
import database.drones_table as drones_table
import database.drone_events_table as drones_event_table
import database.drone_updates_table as drone_zone_data_table
from database.organizations_table import OrgAttributes, create_orga, get_orga, update_orga
from database import settings_table, user_settings_table


MAIL = 'test3@mail.de'
MAIL_TWO = 'test2@mail.de'
MAIL_THREE = 'neuemail@we.de'
pwhash = get_password_hash('dsfsdfdsfsfddfsfd')
testorga = Organization(id=1,name='testorga',abbreviation='TO')
user_one = UserWithSensitiveInfo(email=MAIL,
                first_name='Hans',
                last_name='Dieter',
                hashed_password=pwhash,
                permission=1,
                disabled=0,
                email_verified=0,
                organization= testorga)

user_two = UserWithSensitiveInfo(email=MAIL,
                first_name='Hans',
                last_name='Dieter',
                hashed_password=pwhash,
                permission=1,
                disabled=0,
                email_verified=0,
                organization= testorga)

def test_usertable():
    """tests for user table.
    """
    create_user(user_one)
    fetched_user = get_user(user_one.email)
    assert fetched_user.first_name == user_one.first_name, "Couldnt create or get user"
    for key, value in user_one.__dict__.items():
        if key == 'organization':
            assert fetched_user.__dict__[key].name == value.name, 'Objects not matching'
        else:
            assert fetched_user.__dict__[key] == value, 'Objects not matching'

    update_user(user_one.id,UsrAttributes.FIRST_NAME,'Peter')
    fetched_user = get_user(user_one.email)
    assert fetched_user.first_name == 'Peter', "Couldnt change username"

    update_user(user_one.id,UsrAttributes.EMAIL,MAIL_THREE)
    fetched_user = get_user(user_one.email)
    assert fetched_user is None, "Couldnt change email"
    fetched_user = get_user(MAIL_THREE)
    assert fetched_user.first_name == 'Peter', "Couldnt change email"

    create_user(user_two)
    fetched_user = get_user(MAIL)
    assert fetched_user.first_name == user_two.first_name, "Couldnt create user with first email"
    for key, value in user_two.__dict__.items():
        if key == 'organization':
            assert fetched_user.__dict__[key].name == value.name, 'Objects not matching'
        else:
            assert fetched_user.__dict__[key] == value, 'Objects not matching'


def test_verifytable():
    """tests for mail verification table.
    """
    create_table(CREATE_MAIL_VERIFY_TABLE)
    token = 'ichbineintoken'
    store_token(MAIL,token)
    assert check_token(token) is True, "Couldnt store token"
    assert get_mail_by_token(token) == MAIL, "Mail doesnt match the token"
    assert get_token_by_mail(MAIL) == token, "Couldnt store token"
    token = 'ichbineintoken:)'
    store_token(MAIL,token)
    assert get_token_by_mail(MAIL) == token, "Couldnt update token"

def test_orga():
    """tests for orga table.
    """
    create_orga(testorga.name,testorga.abbreviation)
    orga = get_orga('testorga')
    update_orga(orga,OrgAttributes.ABBREVIATION,'TEO')
    new_name = 'BPORG'
    update_orga(orga,OrgAttributes.NAME,new_name)
    testorga.name = new_name
    orga2 = get_orga(new_name)
    assert orga2 is not None

def test_usersettings():
    """tests for usersettings and settings table.
    """
    user = get_user(MAIL)
    #create tables
    create_table(settings_table.CREATE_SETTINGS_TABLE)
    create_table(user_settings_table.CREATE_USERSETTINGS_TABLE)
    #create settings
    settings_table.create_setting('Test',
                                  'This is a testsetting',
                                  'test',
                                  SettingsType.STRING)
    settings_table.create_setting('Lightmode',
                                  'Lightmode activated or not',
                                  json.dumps({'test':1}),
                                  SettingsType.JSON)
    #get list of all settings
    settinglist = settings_table.get_settings()
    assert len(settinglist)==2
    #set the setting with id 1 for user to 2
    user_settings_table.set_usersetting(1,user_id=user.id,value='ich will das')
    #get the value, which should be 2
    setting = user_settings_table.get_usersetting(1,user.id)
    assert setting.value == 'ich will das', 'Couldnt set value.'
    #set the setting with id 1 for user to 1
    user_settings_table.set_usersetting(1,user_id=user.id,value=1)
    #get the value, which should be 1
    setting = user_settings_table.get_usersetting(1,user.id)
    assert setting.value != 'ich will das', 'Couldnt set value.'

    #set the setting with id 2 for user to {'test':2}
    user_settings_table.set_usersetting(2,user_id=user.id,value=json.dumps({'test':2}))
    usrsetting = user_settings_table.get_usersetting(2,user.id)
    print(usrsetting)
    usrsetting = user_settings_table.get_usersetting(2,3)
    print(usrsetting)



def test_dronetable():
    """tests for drones table.
    """
    #create tables
    create_table(drones_table.CREATE_DRONES_TABLE)
    #create drone
    testdrone = Drone(  id = 4,
                        name="Trinity F90+",
                        type = "Unmanned Aerial Vehicle",
                        flight_range = 100,
                        cc_range = 7.5,
                        flight_time= 90,
                        )
    testdrtwo = Drone(id = 6,
            name='XR-201',
            type = "Unmanned Aerial Vehicle",
            flight_range = 50.7,
            cc_range = 10,
            flight_time= 33,
            #sensors=["Qube 240 LiDAR", "Sony RX1 RII", "MicaSense RedEdge-P", "MicaSense Altum-PT"]
            )
    drone_one = drones_table.create_drone(testdrone.name,
                                          testdrone.type,
                                          testdrone.flight_range,
                                          testdrone.cc_range,
                                          testdrone.flight_time)
    for key, value in testdrone.__dict__.items():
        assert drone_one.__dict__[key] == value, 'Objects not matching'
    try:
        drones_table.create_drone(testdrone.name,None,None,None,None)
        print('IntegrityError should be thrown')
    except sqlite3.IntegrityError:
        pass

    drone_two = drones_table.create_drone(testdrtwo.name,
                                          testdrtwo.type,
                                          testdrtwo.flight_range,
                                          testdrtwo.cc_range,
                                          testdrtwo.flight_time)
    for key, value in testdrtwo.__dict__.items():
        assert drone_two.__dict__[key] == value, 'Objects not matching'

    drones = drones_table.get_drones(1)
    assert len(drones) == 2, 'Something went wrong inserting the Drones.'
    assert drones[0].name == testdrone.name, 'Names not matching. Order wrong?'


def test_dronedatatable():
    """tests for drone updates and drone events table.
    """
    #create tables
    create_table(drone_zone_data_table.CREATE_DRONE_DATA_TABLE)
    create_table(drones_event_table.CREATE_DRONE_EVENT_TABLE)
    #create drone
    testdrone = DroneUpdate(
        drone_id=1,
        timestamp=datetime.datetime.utcnow(),
        longitude=12.68895149,
        latitude=52.07454738,
        flight_range=20.0,
        flight_time=16.4
    )
    time.sleep(1)
    testdatatwo = DroneUpdate(
        drone_id=1,
        timestamp=datetime.datetime.utcnow(),
        longitude=49.888708,
        latitude=8.656927,
        flight_range=20.0,
        flight_time=16.4
    )

    drone_zone_data_table.create_drone_update(
    drone_id=testdrone.drone_id,
    timestamp=testdrone.timestamp,
    longitude=testdrone.lon,
    latitude=testdrone.lat,
    flight_range=testdrone.flight_range,
    flight_time=testdrone.flight_time)

    drone_zone_data_table.create_drone_update(
    drone_id=testdatatwo.drone_id,
    timestamp=testdatatwo.timestamp,
    longitude=testdatatwo.lon,
    latitude=testdatatwo.lat,
    flight_range=testdatatwo.flight_range,
    flight_time=testdatatwo.flight_time)

    drones_event_table.insert_demo_events(long=12.68895149, lat=52.07454738)

@pytest.mark.asyncio
async def test_orgazone():
    """aasync zone api calls tests
    """
    tasks = []
    tasks.append(asyncio.create_task(api_zones.read_zones_all(user_one)))
    tasks.append(asyncio.create_task(api_zones.read_zone('zone_one',user_one)))
    tasks.append(asyncio.create_task(api_zones.read_zone('zone_two',user_one)))
    gathered = await asyncio.gather(*tasks)
    for gath in gathered:
        print(gath)
        print('\n')
