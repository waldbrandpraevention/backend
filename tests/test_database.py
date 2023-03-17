"""database tests"""
# setting path
import json
import os
import random
from sqlite3 import IntegrityError
from api.dependencies.authentication import get_password_hash
from api.dependencies.classes import(Organization,
                                     UserWithSensitiveInfo,
                                     SettingsType)
from database.database import create_table
from database.mail_verif_table import (check_token,
                                       get_mail_by_token,
                                       get_token_by_mail,
                                       store_token,
                                       CREATE_MAIL_VERIFY_TABLE
                                       )
from database.users_table import get_user
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
    try:
        create_orga(testorga.name,testorga.abbreviation)
    except IntegrityError:
        print('Orga already exists')

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
    user = get_user(os.getenv("ADMIN_MAIL"))
    #create tables
    create_table(settings_table.CREATE_SETTINGS_TABLE)
    create_table(user_settings_table.CREATE_USERSETTINGS_TABLE)
    #create settings
    try:
        settings_table.create_setting('Test',
                                    'This is a testsetting',
                                    'test',
                                    SettingsType.STRING)
        settings_table.create_setting('Lightmode',
                                    'Lightmode activated or not',
                                    json.dumps({'test':1}),
                                    SettingsType.JSON)
    except IntegrityError:
        print('Setting already exists')

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

    #set the setting with id 2 for user to {'test':random_int}
    test_int = random.randint(1,100)

    test_str = f'test{test_int}'
    user_settings_table.set_usersetting(1,user_id=user.id,value=test_str)
    usrsetting = user_settings_table.get_usersetting(1,user.id)
    assert usrsetting.value == test_str, 'Couldnt set value.'

    test_json = json.dumps({'test':test_int})
    user_settings_table.set_usersetting(2,user_id=user.id,value=json.dumps(test_json))
    usrsetting = user_settings_table.get_usersetting(2,user.id)
    assert usrsetting.value == test_json, 'Couldnt set value.'
