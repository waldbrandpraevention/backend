
from classes import User, UserWithSensitiveInfo
from database.database import create_table
from database.mail_verif_table import check_token, get_mail_by_token, get_token_by_mail, store_token, CREATE_MAIL_VERIFY_TABLE
from database.users_table import create_user,get_user,CREATE_USER_TABLE
import time 

mail = 'test@mail.de'

def test_usertable():
    create_table(CREATE_USER_TABLE)
    user = UserWithSensitiveInfo(email=mail,
                first_name='Hans',
                last_name='Dieter',
                hashed_password='dsfsdfdsfsfddfsfd',
                permission=1,
                disabled=0,
                email_verified=0)
    create_user(user)
    user = get_user(mail)
    #print(user)

def test_verifytable():
    create_table(CREATE_MAIL_VERIFY_TABLE)
    token = 'ichbineintoken.:)'
    store_token(mail,token)
    store_token(mail,token, update=True)
    print(check_token(token))
    print(get_mail_by_token(token))
    print(get_token_by_mail(mail))
    

start = time.time()
[test_usertable() for _ in range(500)]
test_verifytable()
end = time.time()
print(end - start)
