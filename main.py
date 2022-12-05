from datetime import datetime, timedelta
from enum import Enum
from fastapi import Depends, FastAPI, HTTPException, status, Request, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

import random
from validation import *

#secret key generated with: openssl rand -hex 32
#should not be included dn the public repo in the final build
SECRET_KEY = "cbdc851fece93e7b1a3bf9ca16c9ce62939e22f668866c875d294363e2530b27"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS = 24

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None

class Permission(Enum):
    USER = 1
    ADMIN = 2
    THIRD_PARTY = 3

class User(BaseModel):
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None

class UserWithSensitiveInfo(User):
    hashed_password: str
    permission: Permission | None = None
    disabled: bool | None = None
    email_verified: bool

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()

def is_admin(user: User):
    return user.permission == Permission.ADMIN

def verify_password(plain_password, hashed_password):
    """Checks if a plain password matches a given hash

    Args:
        plain_password (str): Plain text password
        hashed_password (str): hashed password

    Returns:
        bool: True if the hashes match
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """Returns the hash of the given pssward

    Args:
        password (str): Plain text password

    Returns:
        str: hash
    """
    return pwd_context.hash(password)


def get_user(email: str):
    """Creates a user object from the information in the db

    Args:
        email (str): Email of the user

    Returns:
        User: User object filled with the user information
        None: if no user exists with the given email
    """

    #Pseudocode
    # if user exists:
    #   create and return a UserWithPassword object (class from above, all values need te be initialized, includung the ones from the base user class)
    # else:
    #   return None
    return None

async def send_email():
    return true


def authenticate_user(email: str, password: str):
    """Creates a user if the given password matches the users password

    Args:
        email (str): Email of the user
        password (str): Plaintext password

    Returns:
        User: Authenticated user
        None: If user does not exists or the passowrd is wrong
    """
    user = get_user(email)
    if user and verify_password(password, user.hashed_password):
        return user
    return None

def create_access_token(data: dict, expires_delta: timedelta):
    """Creates an access token with an expiration time

    Args:
        data (dict): Data to encode

        expires_delta (timedelta): Time till expiration

    Returns:
        str: token
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_email_from_token(token: str = Depends(oauth2_scheme)):
    """Returns the email in the token

    Args:
        token str: Usertoken to decode

    Raises:
        HTTPException: Raises error if the token has no email or the token is invalid or expired

    Returns:
        str: email that is embedded in the token
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token has no information",
            )
        token_data = TokenData(email=email)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Token is expired",
        )
    return token_data.email

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """_summary_

    Args:
        token (str, optional): _description_. Defaults to Depends(oauth2_scheme).

    Raises:
        credentials_exception: Raises error if the token is invalid
        disabled_exception: Raises error if the user is disabled
        email_verification_exception: Raises orror if the email of the user did not get verified yet

    Returns:
        User: User object of the current user
    """
    disabled_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="User is disabled",
        headers={"WWW-Authenticate": "Bearer"},
    )
    email_verification_exception = HTTPException(
        status_code=status.HTTP_406_NOT_ACCEPTABLE,
        detail="Email is not verified",
    )
    email = await get_email_from_token(token)
    user = get_user(email)
    if user is None:
        raise credentials_exception
    if user.disabled:
        raise disabled_exception
    if not user.verified_email:
        raise email_verification_exception
    return user


@app.post("/user/token/", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """API call to create an access token

    Args:
        form_data (OAuth2PasswordRequestForm, optional): Login data. Defaults to Depends().

    Raises:
        HTTPException: Raises error if the email or password or incorrect

    Returns:
        dict: Token information in json format
    """
    
    #note: username is the reserved name for the login name, must be used even if we are using email
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me/", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """API call to get the curret user we are communicating with

    Args:
        current_user (User, optional): User. Defaults to Depends(get_current_user).

    Returns:
        User: Current user with only the basic infos (no password)
    """
    return current_user

@app.get("/")
async def root():
    n1 = random.randint(0,100)
    n2 = random.randint(0,100)
    raise HTTPException(
                status_code=status.HTTP_418_IM_A_TEAPOT,
                detail="Random addition: " + str(n1) + " + " + str(n2) + " = " + str(n1 +n2),
            )


#test stuff
@app.get("/static/test/all")
async def read_static_test_all():
    return [{"static_info": "This is the same for everyone. Even people that are not logged in yet."}]

@app.get("/static/test/authenticated")
async def read_static_test_auth(current_user: User = Depends(get_current_user)):
    return [{"static_info": "This is the same for everyone that is logged in"}]

@app.post("/register/", status_code=status.HTTP_201_CREATED)
async def register(email: str = Form(), password: str = Form(), first_name: str = Form(), last_name: str = Form()):
    errors = []
    validate_email(email)
    errors.append(validate_password(password))
    errors.append(validate_first_name(first_name))
    errors.append(validate_last_name(last_name))
    if len(errors) > 0:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail=errors,
        )
    if get_user(email):
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="This email is already assosiated with an existing account",
        )
    #add user to db
    return {"message": "success"}

@app.post("/email-verification/verify/", status_code=status.HTTP_200_OK)
async def verify_email(token: str):
    invalid_token_exception = HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Token invalid",
        )

    exists = true #check if db has given code
    if not exists:
        raise invalid_token_exception

    try:
        token_email = await get_email_from_token(token)
    except HTTPException as e:
        if e.status_code == status.HTTP_406_NOT_ACCEPTABLE: #expired
            mail_from_token = "" #get from db with token
            new_token = create_access_token(mail_from_token, timedelta(hours=EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS))
            await send_email(new_token) #placeholder
            #change token in db
            #if sending successfull...
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="Token expired. A new email is on it's way",
            )
        else:
            raise invalid_token_exception
    db_token = "" #token from db via mail
    if true: #not in db, should never happen but just in case
        raise invalid_token_exception
    if token != db_token: 
        raise invalid_token_exception
    #delete token from db
    user = get_user(token_email)
    user.verified_email = true
    return {"message": "Email successfully verified"}