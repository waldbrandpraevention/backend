from smtplib import SMTP
import datetime
import validation

server = os.getenv("SMTP_Host")
port = os.getenv("SMTP_Port")
user = os.getenv("SMTP_User")
passsword = os.getenv("SMTP_Password")
sender = os.getenv("SMTP_Sender")


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