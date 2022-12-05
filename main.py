from datetime import datetime, timedelta
from enum import Enum
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel


#secret key generated with: openssl rand -hex 32
SECRET_KEY = "cbdc851fece93e7b1a3bf9ca16c9ce62939e22f668866c875d294363e2530b27"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


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
    permission: Permission | None = None
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    disabled: bool | None = None

class ThirdParty(BaseModel):
    name: str
    permission: Permission | None = None

class UserWithPassword(User):
    hashed_password: str

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


def create_access_token(data: dict):
    """Creates an access token with a expiration time of 30min

    Args:
        data (dict): Data to encode

    Returns:
        str: access token
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Returns the current user that we comunicating with

    Args:
        token str: Usertoken to identify the user

    Raises:
        credentials_exception: Raises error if the token is invalid
        disabled_exception: Raises error if the user is disabled

    Returns:
        User: Current user object
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    disabled_exception = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="User is disabled",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = get_user(token_data.email)
    if user is None:
        raise credentials_exception
    if current_user.disabled:
        raise disabled_exception
    return user


@app.post("/user/token", response_model=Token)
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


#test stuff
@app.get("/static/test/all")
async def read_static_test_all():
    return [{"static_info": "This is the same for everyone. Even people that are not logged in yet."}]

@app.get("/static/test/authenticated")
async def read_static_test_auth(current_user: User = Depends(get_current_user)):
    return [{"static_info": "This is the same for everyone that is logged in"}]

@app.post("/drone/token", response_model=Token)
async def create_drone_access_token(form_data: OA = Depends()):
    current_user: User = Depends(get_current_user)
    if not is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is not an adim",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return None