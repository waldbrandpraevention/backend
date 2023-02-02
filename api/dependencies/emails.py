from smtplib import SMTP
import datetime
from validation import *
import os
from fastapi import Depends, FastAPI, HTTPException, status
from .authentication import create_access_token, EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS
from datetime import timedelta

server = os.getenv("SMTP_HOST")
port = os.getenv("SMTP_PORT")
user = os.getenv("SMTP_USER")
passsword = os.getenv("SMTP_PASSWORD")
sender = os.getenv("SMTP_SENDER")

async def send_token_email(reciever: str):

    access_token_expires = timedelta(hours=EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS)
    access_token = create_access_token(
        data={"sub": reciever}, expires_delta=access_token_expires
    )
    message = """
    Bitte klicken Sie auf den Link:\n
    https://kiwa.tech/api/email/verify/?token=%s
    """ % (message, access_token)

    return await send_email(reciever, "Ihr neure KIWA Account", message)


async def send_email(reciever: str, subject: str, message: str):

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

    message = """\
    From: %s\n
    To: %s\n
    Subject: %s\n

    %s
    """ % (sender, reciever, subject, message)

    email_server = SMTP(server, port)
    email_server.login(user, passsword)
    email_server.sendmail(sender, reciever, message)
    email_server.quit()

    return {"message": "Email code executed"}