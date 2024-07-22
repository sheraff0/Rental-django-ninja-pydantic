from bs4 import BeautifulSoup

from api.assets import attachments_dict

from django.conf import settings
from django.core.mail import EmailMultiAlternatives


def send_mail(subject, body, to, attachments=None):
    _text = body
    try:
        soup = BeautifulSoup(body, "html.parser")
        _text = soup.text
    except: ...
    _attachments = attachments and [_a for x in attachments if
        (_a := attachments_dict.get(x) if type(x) == str else x)]
    message = EmailMultiAlternatives(subject, _text,
        from_email=settings.EMAIL_HOST_USER, to=to, attachments=_attachments)
    message.attach_alternative(body, "text/html")
    message.send()
