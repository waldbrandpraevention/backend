
# setting path
import os
import sys

sys.path.append('../backend')
from api.dependencies.authentication import get_password_hash
from api.dependencies.classes import User, UserWithSensitiveInfo
from database.database import DATABASE_PATH, create_table
from database.mail_verif_table import check_token, get_mail_by_token, get_token_by_mail, store_token, CREATE_MAIL_VERIFY_TABLE
from database.users_table import create_user,get_user,CREATE_USER_TABLE
from database.users_table import UsrAttributes, create_user,get_user,CREATE_USER_TABLE, update_user
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
                organization = 1)

user_two = UserWithSensitiveInfo(email=mail,
                first_name='Hans',
                last_name='Dieter',
                hashed_password=pwhash,
                permission=1,
                disabled=0,
                email_verified=0,
                organization = 1)

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
    print(orga)
    print(orga2)

def test_usersettings():
    user = get_user(mail)
    create_table(settings_table.CREATE_SETTINGS_TABLE)
    create_table(user_settings.CREATE_USERSETTINGS_TABLE)
    index = settings_table.create_setting('Test','This is a testsetting',defaul_val=0)
    index = settings_table.create_setting('Lightmode','Lightmode activated or not',defaul_val=1)
    settinglist = settings_table.get_settings()
    print(settinglist)
    if not index:
        index = 1
    user_settings.set_usersetting(index,user_id=user.id,value=2)
    value = user_settings.get_usersetting(index,user.id)
    print(value)
    user_settings.set_usersetting(index,user_id=user.id,value=1)
    value = user_settings.get_usersetting(index,user.id)
    print(value)
    
try:
    os.remove(DATABASE_PATH)
except: 
    pass

start = time.time()
test_usertable() #for _ in range(500)]
test_verifytable()
test_orga()
end = time.time()
print(end - start)
