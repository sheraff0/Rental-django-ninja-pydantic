from config.celery import app

from contrib.utils.email import send_mail


@app.task
def send_mail_task(subject, body, to, attachments=None):
    try:
        send_mail(subject, body, to, attachments=attachments)
    except: ...
