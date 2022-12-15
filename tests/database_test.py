
# setting path
import sys
sys.path.append('../backend')
from api.dependencies.classes import User, UserWithSensitiveInfo
from database.database import create_table
from database.mail_verif_table import check_token, get_mail_by_token, get_token_by_mail, store_token, CREATE_MAIL_VERIFY_TABLE
from database.users_table import create_user,get_user,CREATE_USER_TABLE
from database.users_table import UsrAttributes, create_user,get_user,CREATE_USER_TABLE, update_user
from database.organizations import CREATE_ORGANISATIONS_TABLE, OrgAttributes, create_orga, get_orga, update_orga
import time 

mail = 'test@mail.de'
mail2 = 'test2@mail.de'
mail3 = 'neuemail@we.de'

def test_usertable():
    create_table(CREATE_USER_TABLE)
    userone = UserWithSensitiveInfo(email=mail,
                first_name='Hans',
                last_name='Dieter',
                hashed_password='dsfsdfdsfsfddfsfd',
                permission=1,
                disabled=0,
                email_verified=0,
                organization = 1)
    create_user(userone)
    user = UserWithSensitiveInfo(email=mail,
                first_name='Hans',
                last_name='Dieter',
                hashed_password='dsfsdfdsfsfddfsfd',
                permission=1,
                disabled=0,
                email_verified=0,
                organization = 1)
    create_user(user)
    update_user(userone,UsrAttributes.FIRST_NAME,'Peter')
    update_user(userone,UsrAttributes.EMAIL,mail3)
    user = get_user(mail3)
    print(user)

def test_verifytable():
    create_table(CREATE_MAIL_VERIFY_TABLE)
    token = 'ichbineintoken:)'
    store_token(mail,token)
    store_token(mail,token)
    print(check_token(token))
    print(get_mail_by_token(token))
    print(get_token_by_mail(mail))

def test_orga():
    create_table(CREATE_ORGANISATIONS_TABLE)
    create_orga('testorga','TO')
    orga = get_orga('testorga')
    update_orga(orga,OrgAttributes.ABBREVIATION,'TEO')
    update_orga(orga,OrgAttributes.NAME,'BPORG')
    orga2 = get_orga('BPORG')
    print(orga)
    print(orga2)
    

start = time.time()
test_usertable() #for _ in range(500)]
#test_verifytable()
end = time.time()
print(end - start)
