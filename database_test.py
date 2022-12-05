
from classes import User, UserWithSensitiveInfo
from database.database import create_table
from database.users_table import create_user,get_user

CREATE_USER_TABLE = """ CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY,
                        email TEXT NOT NULL UNIQUE,
                        first_name TEXT NOT NULL,
                        last_name TEXT NOT NULL,
                        hashed_password TEXT NOT NULL,
                        permission INTEGER DEFAULT 0,
                        disabled INTEGER,
                        email_verified INTEGER NOT NULL
                    );"""

create_table(CREATE_USER_TABLE)
user = UserWithSensitiveInfo(email='test@mail.de',
            first_name='Hans',
            last_name='Dieter',
            hashed_password='dsfsdfdsfsfddfsfd',
            permission=1,
            disabled=0,
            email_verified=0)
create_user(user)
user = get_user('test@mail.de')
print(user)