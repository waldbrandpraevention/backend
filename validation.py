
import re

#return list of errors on each function

EMAIL_REGEX = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")

def validate_email(email: str):
    err = []
    if not re.fullmatch(EMAIL_REGEX, email):
        err.append("Email uses invalid syntax")
    return err

def validate_password(password: str):
    err = []
    if len(password) < 8:
        err.append("Password must be at least 8 characters long")
    if re.search('[0-9]', password) is None:
            err.append("Password must have at least one number")
    if re.search('[A-Z]', password) is None: 
            err.append("Password must have at least one uppercase character")
    if re.search('[a-z]', password) is None: 
            err.append("Password must have at least one lowercase character")
    return err

def validate_first_name(first_name: str):
    err = []
    if len(first_name) == 0:
        err.append("Last name can't be empty")
    return err

def validate_last_name(last_name: str):
    err = []
    if len(last_name) == 0:
        err.append("First name can't be empty")
    return err

def validate_organization(last_name: str):
    err = []
    if len(last_name) == 0:
        err.append("Organization can't be empty")
    return err