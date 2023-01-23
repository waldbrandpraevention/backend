from smtplib import SMTP
import datetime
import validation
import os
from fastapi import Depends, FastAPI, HTTPException, status

server = os.getenv("SMTP_HOST")
port = os.getenv("SMTP_PORT")
user = os.getenv("SMTP_USER")
passsword = os.getenv("SMTP_PASSWORD")
sender = os.getenv("SMTP_SENDER")


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
    From: %s
    To: %s
    Subject: %s

    %s
    """ % (sender, reciever, subject, message)

    email_server = smtplib.SMTP(server, port)
    email_server.login(user, passsword)
    email_server.sendmail(sender, reciever, message)
    email_server.quit()

    return {"message": "Email code executed"}