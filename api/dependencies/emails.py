"""Futctions for email communication"""
import os
from smtplib import SMTP
from datetime import timedelta
from fastapi import HTTPException, status
from validation import validate_email
from .authentication import create_access_token, EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS

server = os.getenv("SMTP_HOST")
port = os.getenv("SMTP_PORT")
user = os.getenv("SMTP_USER")
passsword = os.getenv("SMTP_PASSWORD")
sender = os.getenv("SMTP_SENDER")
domain = os.getenv("DOMAIN_API")

async def send_token_email(reciever: str):
    """Sends out a new token email

    Args:
        reciever (str): Email of the reciever

    Returns:
        Dict: Response
    """

    access_token_expires = timedelta(hours=EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS)
    access_token = create_access_token(
        data={"sub": reciever}, expires_delta=access_token_expires
    )
    message = f"""
    Bitte klicken Sie auf den Link:\n
    {domain}/email/verify/?token={access_token}
    """

    return await send_email(reciever, "KIWA Information", message)


async def send_email(reciever: str, subject: str, message: str):
    """Sends out a new email

    Args:
        reciever (str): Email of the reciever
        subject (str): Subject of the email
        message (str): Message of the email

    Returns:
        Dict: Response
    """

    errors = validate_email(reciever)
    if len(errors) > 0:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Invalid Email",
        )

    if len(subject) == 0:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Email subject must not be empty",
        )

    if len(message) == 0:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Email message must not be empty",
        )

    message_final = f"""\
    From:{sender}\n
    To:{reciever}\n
    Subject:{subject}\n
    {message}
    %s
    """

    email_server = SMTP(server, port)
    email_server.login(user, passsword)
    email_server.sendmail(sender, reciever, message_final)
    email_server.quit()

    return {"message": "Email code executed"}
