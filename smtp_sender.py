from config import *

import errno
import os
import signal
import smtplib
from functools import wraps
from loguru import logger

class TimeoutError(Exception):
    pass

def timeout(seconds=10, error_message=os.strerror(errno.ETIME)):
    def decorator(func):
        def _handle_timeout(signum, frame):
            raise TimeoutError(error_message)

        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
            return result

        return wraps(func)(wrapper)

    return decorator

# @timeout()
def send_email(to, subject, body):
    try:
        port = 587
        smtp = smtplib.SMTP('smtp.gmail.com', port)
        msg = f"Subject: {subject}\r\n\r\n{body}"
        smtp.ehlo() # for tls add this line
        smtp.starttls() # for tls add this line
        smtp.ehlo() # for tls add this line
        smtp.login(GMAIL_EMAIL, GMAIL_PASSWORD)
        smtp.sendmail(GMAIL_EMAIL, to, msg)
        smtp.quit()
    except Exception as e:
        print(e)


if __name__ == '__main__':
    to = ['riyad.parvez@gmail.com',]
    subject = 'OMG Super Important Message'
    body = "Hey, what's up?\n\n- You"
    send_email(to, subject, body)
