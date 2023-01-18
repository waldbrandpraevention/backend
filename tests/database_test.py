
# setting path
import asyncio
import datetime
import json
import os
import sqlite3
import sys
sys.path.append('../backend')
from api.dependencies.drones import get_all_drones
from api.dependencies.authentication import get_password_hash
from api.dependencies.classes import Drone, DroneEvent, EventType, Organization, User,DroneUpdate, UserWithSensitiveInfo,SettingsType
from database.database import DATABASE_PATH, create_table
from database.mail_verif_table import check_token, get_mail_by_token, get_token_by_mail, store_token, CREATE_MAIL_VERIFY_TABLE
from database.users_table import create_user,get_user,CREATE_USER_TABLE
from database.users_table import UsrAttributes, create_user,get_user,CREATE_USER_TABLE, update_user
import database.drones_table as drones_table
import database.drone_events_table as drones_event_table
import database.drone_updates_table as drone_zone_data_table
import database.zones_table as zone_table
from database.organizations_table import CREATE_ORGANISATIONS_TABLE, OrgAttributes, create_orga, get_orga, update_orga
from database import settings_table, user_settings_table
import time 

mail = 'test@mail.de'
mail2 = 'test2@mail.de'
mail3 = 'neuemail@we.de'
pwhash = get_password_hash('dsfsdfdsfsfddfsfd')
testorga = Organization(id=1,name='testorga',abbreviation='TO')
user_one = UserWithSensitiveInfo(email=mail,
                first_name='Hans',
                last_name='Dieter',
                hashed_password=pwhash,
                permission=1,
                disabled=0,
                email_verified=0,
                organization= testorga)

user_two = UserWithSensitiveInfo(email=mail,
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
    create_table(CREATE_USER_TABLE)
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

    update_user(user_one.id,UsrAttributes.EMAIL,mail3)
    fetched_user = get_user(user_one.email)
    assert fetched_user == None, "Couldnt change email"
    fetched_user = get_user(mail3)
    assert fetched_user.first_name == 'Peter', "Couldnt change email"

    create_user(user_two)
    fetched_user = get_user(mail)
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
    store_token(mail,token)
    assert check_token(token) == True, "Couldnt store token"
    assert get_mail_by_token(token) == mail, "Mail doesnt match the token"
    assert get_token_by_mail(mail) == token, "Couldnt store token"
    token = 'ichbineintoken:)'
    store_token(mail,token)
    assert get_token_by_mail(mail) == token, "Couldnt update token"

def test_orga():
    """tests for orga table.
    """
    create_table(CREATE_ORGANISATIONS_TABLE)
    create_orga(testorga.name,testorga.abbreviation)
    orga = get_orga('testorga')
    update_orga(orga,OrgAttributes.ABBREVIATION,'TEO')
    new_name = 'BPORG'
    update_orga(orga,OrgAttributes.NAME,new_name)
    testorga.name = new_name
    orga2 = get_orga(new_name)

def test_usersettings():
    """tests for usersettings and settings table.
    """
    user = get_user(mail)
    #create tables
    create_table(settings_table.CREATE_SETTINGS_TABLE)
    create_table(user_settings_table.CREATE_USERSETTINGS_TABLE)
    #create settings
    index = settings_table.create_setting('Test','This is a testsetting','test', SettingsType.STRING)
    index = settings_table.create_setting('Lightmode','Lightmode activated or not',json.dumps({'test':1}),SettingsType.JSON)
    #get list of all settings
    settinglist = settings_table.get_settings()
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
    testdrone = Drone(  id = 1,
                        name="Trinity F90+",
                        droneowner_id= None,
                        type = "Unmanned Aerial Vehicle",
                        flight_range = 100,
                        cc_range = 7.5,
                        flight_time= 90,
                        #sensors=["Qube 240 LiDAR", "Sony RX1 RII", "MicaSense RedEdge-P", "MicaSense Altum-PT"]
                        )
    testdrtwo = Drone(id = 2,
            name='XR-201',
            droneowner_id= None,
            type = "Unmanned Aerial Vehicle",
            flight_range = 50.7,
            cc_range = 10,
            flight_time= 33,
            #sensors=["Qube 240 LiDAR", "Sony RX1 RII", "MicaSense RedEdge-P", "MicaSense Altum-PT"]
            )
    drone_one = drones_table.create_drone(testdrone.name,testdrone.droneowner_id,testdrone.type,testdrone.flight_range,testdrone.cc_range,testdrone.flight_time)
    for key, value in testdrone.__dict__.items():
        assert drone_one.__dict__[key] == value, 'Objects not matching'
    try:
        drones_table.create_drone(testdrone.name,None,None,None,None,None)
        print('IntegrityError should be thrown')
    except sqlite3.IntegrityError:
        pass

    drone_two = drones_table.create_drone(testdrtwo.name,testdrtwo.droneowner_id,testdrtwo.type,testdrtwo.flight_range,testdrtwo.cc_range,testdrtwo.flight_time)
    for key, value in testdrtwo.__dict__.items():
        assert drone_two.__dict__[key] == value, 'Objects not matching'

    drones = drones_table.get_drones()
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
        longitude=89.156998,
        latitude=90.156998,
        flight_range=20.0,
        flight_time=16.4
    )
    testevent = DroneEvent(
        drone_id=1,
        timestamp=datetime.datetime.utcnow(),
        longitude=89.156998,
        latitude=90.156998,
        event_type=EventType.SMOKE,
        confidence=78,
        picture_path=None,
        ai_predictions=None,
        csv_file_path=None
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
    longitude=testdrone.longitude,
    latitude=testdrone.latitude,
    flight_range=testdrone.flight_range,
    flight_time=testdrone.flight_time)

    drone_zone_data_table.create_drone_update(
    drone_id=testdatatwo.drone_id,
    timestamp=testdatatwo.timestamp,
    longitude=testdatatwo.longitude,
    latitude=testdatatwo.latitude,
    flight_range=testdatatwo.flight_range,
    flight_time=testdatatwo.flight_time)

    drones_event_table.create_drone_event_entry(
        drone_id=testevent.drone_id,
        timestamp=testevent.timestamp,
        longitude=testevent.longitude,
        latitude=testevent.latitude,
        event_type=testevent.event_type.value,
        confidence=testevent.confidence,
        picture_path=testevent.picture_path,
        ai_predictions=testevent.ai_predictions,
        csv_file_path=testevent.csv_file_path
    )

    output = drone_zone_data_table.get_drone_data_by_timestamp(1,datetime.datetime.utcnow()-datetime.timedelta(minutes=5))
    assert len(output) == 2, 'Something went wrong inserting the Data (2).'
    assert output[0].latitude == testdrone.latitude, 'Something went wrong with creating geo Point for testdrone.'
    for key, value in testdrone.__dict__.items():
        assert output[0].__dict__[key] == value, 'Objects not matching'
    output = drone_zone_data_table.get_drone_data_by_timestamp(1,testdatatwo.timestamp-datetime.timedelta(seconds=1))
    assert len(output) == 1, 'Something went wrong inserting the Data (1).'

    output = drones_event_table.get_drone_event_by_timestamp(1)
    assert len(output) == 1, 'Something went wrong inserting the Data (2).'
    assert output[0].latitude == testdrone.latitude, 'Something went wrong with creating geo Point for testdrone.'
    
def test_zone():
    """tests for zone table.
    """
    create_table(zone_table.CREATE_ZONE_TABLE)
    zone_one_coord = [[84.23,181.82], [168.32 ,117.5], [103.7 ,58.953], [40.23 ,108.82]]
    zone_table.create_zone('zone_one',zone_one_coord)
    zone_table.create_zone('zone_two',[[184.23,281.82], [268.32 ,217.5], [203.7 ,158.953], [140.23 ,208.82]])
    outpu = zone_table.get_zones()
    assert outpu[0].coordinates == zone_one_coord, "Zone cord not matching"
    assert zone_table.get_zone_of_coordinate(89.156998,90.156998) != None, "Point is in square"
    assert zone_table.get_zone_of_coordinate(85.156998,61.156998) == None, "Point is not in square"
    assert zone_table.get_zone_of_coordinate(148.156998,119.156998) != None, "Point is in square"
    assert zone_table.get_zone_of_coordinate(159.156998,138.156998) == None, "Point is not in square"



try:
    os.remove(DATABASE_PATH)
except Exception as e: 
    print(e)

start = time.time()
test_orga()
test_usertable() #for _ in range(500)]
test_verifytable()
test_usersettings()
# test_dronetable()
# test_dronedatatable()
# test_zone()

end = time.time()
print(end - start)
