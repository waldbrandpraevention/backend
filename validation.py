"""functions for validaten"""
import re
from api.dependencies.classes import Permission

#return list of errors on each function

EMAIL_REGEX = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")

def validate_email(email: str):
    """validates email

    Args:
        email (str): email to validate

    Returns:
        str array: error list
    """
    err = []
    if not re.fullmatch(EMAIL_REGEX, email):
        err.append("Email uses invalid syntax")
    return err

def validate_password(password: str):
    """validates passwords

    Args:
        passowrd (str): password to validate

    Returns:
        str array: error list
    """
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
    """validates first names

    Args:
        first_name (str): name to validate

    Returns:
        str array: error list
    """
    err = []
    if len(first_name) == 0:
        err.append("First name can't be empty")
    return err

def validate_last_name(last_name: str):
    """validates first names

    Args:
        last_name (str): name to validate

    Returns:
        str array: error list
    """
    err = []
    if len(last_name) == 0:
        err.append("Last name can't be empty")
    return err

def validate_organization(org_name: str):
    """validates organizations

    Args:
        org_name (str): orga to validate

    Returns:
        str array: error list
    """
    err = []
    if len(org_name) == 0:
        err.append("Organization can't be empty")
    return err

def validate_permission(permission_int: int):
    """validates permissions

    Args:
        permission_int (str): orga to validate

    Returns:
        str array: error list
    """
    err = []
    if not permission_int in Permission.list():
        err.append("Permission doesnt exist.")
    return err
