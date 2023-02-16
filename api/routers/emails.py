"""Code for email api"""

from fastapi import HTTPException, status, APIRouter
from ..dependencies.authentication import get_email_from_token
from ..dependencies.users import get_user

from ..dependencies.emails import (
    send_token_email
    )

router = APIRouter()

@router.get("/email/verify/", status_code=status.HTTP_200_OK)
async def verify_email(token: str):
    """Validates a token that got send with an email

    Args:
        token (str): token to verity

    Raises:
        HTTPException: misc error
        invalid_token_exception: token is not valid

    Returns:
        response message
    """
    invalid_token_exception = HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Token invalid",
        )
    expried_token_exception = HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Token expired. A new email is on it's way",
        )

    try:
        token_email = await get_email_from_token(token, False)
    except HTTPException as err:
        if err.status_code == status.HTTP_406_NOT_ACCEPTABLE: #expired
            mail_from_token = await get_email_from_token(token, True)
            await send_token_email(mail_from_token)
            raise expried_token_exception from err
        raise invalid_token_exception from err

    user = get_user(token_email)
    user.email_verified = True
    return {"message": "Email successfully verified"}
