
# setting path
import datetime
import os
import sys

sys.path.append('../backend')
from api.dependencies.authentication import get_password_hash
from api.dependencies.classes import Drone, User, UserWithSensitiveInfo
from database.database import DATABASE_PATH, create_table
from database.mail_verif_table import check_token, get_mail_by_token, get_token_by_mail, store_token, CREATE_MAIL_VERIFY_TABLE
from database.users_table import create_user,get_user,CREATE_USER_TABLE
from database.users_table import UsrAttributes, create_user,get_user,CREATE_USER_TABLE, update_user
import database.drones as drones_table
from database.organizations import CREATE_ORGANISATIONS_TABLE, OrgAttributes, create_orga, get_orga, update_orga
from database import settings_table, user_settings
import time 

mail = 'test@mail.de'
mail2 = 'test2@mail.de'
mail3 = 'neuemail@we.de'
pwhash = get_password_hash('dsfsdfdsfsfddfsfd')
user_one = UserWithSensitiveInfo(email=mail,
                first_name='Hans',
                last_name='Dieter',
                hashed_password=pwhash,
                permission=1,
                disabled=0,
                email_verified=0,
                organization_id = 1)

user_two = UserWithSensitiveInfo(email=mail,
                first_name='Hans',
                last_name='Dieter',
                hashed_password=pwhash,
                permission=1,
                disabled=0,
                email_verified=0,
                organization_id = 1)

def test_usertable():
    create_table(CREATE_USER_TABLE)
    create_user(user_one)
    fetched_user = get_user(user_one.email)
    assert fetched_user.first_name == user_one.first_name, "Couldnt create or get user"

    update_user(user_one,UsrAttributes.FIRST_NAME,'Peter')
    fetched_user = get_user(user_one.email)
    assert fetched_user.first_name == 'Peter', "Couldnt change username"

    update_user(user_one,UsrAttributes.EMAIL,mail3)
    fetched_user = get_user(user_one.email)
    assert fetched_user == None, "Couldnt change email"
    fetched_user = get_user(mail3)
    assert fetched_user.first_name == 'Peter', "Couldnt change email"

    create_user(user_two)
    fetched_user = get_user(mail)
    assert fetched_user.first_name == user_two.first_name, "Couldnt create user with first email"


def test_verifytable():
    create_table(CREATE_MAIL_VERIFY_TABLE)
    token = 'ichbineintoken:)'
    store_token(mail,token)
    store_token(mail,token)
    assert check_token(token) == True, "Couldnt store token"
    assert get_mail_by_token(token) == mail, "Mail doesnt match the token"
    assert get_token_by_mail(mail) == token, "Couldnt store token"

def test_orga():
    create_table(CREATE_ORGANISATIONS_TABLE)
    create_orga('testorga','TO')
    orga = get_orga('testorga')
    update_orga(orga,OrgAttributes.ABBREVIATION,'TEO')
    update_orga(orga,OrgAttributes.NAME,'BPORG')
    orga2 = get_orga('BPORG')

def test_usersettings():
    user = get_user(mail)
    #create tables
    create_table(settings_table.CREATE_SETTINGS_TABLE)
    create_table(user_settings.CREATE_USERSETTINGS_TABLE)
    #create settings
    index = settings_table.create_setting('Test','This is a testsetting',defaul_val=0)
    index = settings_table.create_setting('Lightmode','Lightmode activated or not',defaul_val=1)
    #get list of all settings
    settinglist = settings_table.get_settings()
    if not index:
        index = 1
    #set the setting with id 1 for user to 2
    user_settings.set_usersetting(index,user_id=user.id,value=2)
    #get the value, which should be 2
    value = user_settings.get_usersetting(index,user.id)
    assert value == 2, 'Couldnt set value.'
    #set the setting with id 1 for user to 1
    user_settings.set_usersetting(index,user_id=user.id,value=1)
    #get the value, which should be 1
    value = user_settings.get_usersetting(index,user.id)
    assert value == 1, 'Couldnt set value.'


def test_dronetable():
    #create tables
    create_table(drones_table.CREATE_DRONES_TABLE)
    #create drone
    testdrone = Drone(id = 1,
            name='XR-200',
            droneowner_id= None,
            last_update=datetime.datetime.now(),
            last_longitude=49.878708,
            last_latitude=8.646927)
    testdrtwo = Drone(id = 2,
            name='XR-201',
            droneowner_id= None,
            last_update=datetime.datetime.now(),
            last_longitude=49.878708,
            last_latitude=8.646927)
    drone_one = drones_table.create_drone(testdrone.name,testdrone.droneowner_id,testdrone.last_update,testdrone.last_longitude,testdrone.last_latitude)
    for key, value in testdrone.__dict__.items():
        assert drone_one.__dict__[key] == value, 'Objects not matching'
    should_be_none = drones_table.create_drone('XR-200',None,datetime.datetime.now(),49.878708,8.646927)
    assert should_be_none== None, 'Unique Name failed.'

    drone_two = drones_table.create_drone(testdrtwo.name,testdrtwo.droneowner_id,testdrtwo.last_update,testdrtwo.last_longitude,testdrtwo.last_latitude)
    for key, value in testdrtwo.__dict__.items():
        assert drone_two.__dict__[key] == value, 'Objects not matching'

    drones = drones_table.get_drones()
    assert len(drones) == 2, 'Something went wrong inserting the Drones.'
    assert drones[0].name == testdrone.name, 'Names not matching. Order wrong?'

    
try:
    os.remove(DATABASE_PATH)
except Exception as e: 
    print(e)

start = time.time()
test_usertable() #for _ in range(500)]
test_verifytable()
test_orga()
test_usersettings()
test_dronetable()
end = time.time()
print(end - start)
