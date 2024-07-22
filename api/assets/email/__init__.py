import os
import base64
from pathlib import Path

from email.mime.image import MIMEImage

ASSETS_PATH = Path("api/assets")
EMAIL_IMAGES_PATH = ASSETS_PATH / "email/img"


attachments_dict = {}
for filename in os.listdir(str(EMAIL_IMAGES_PATH)):
    with open(EMAIL_IMAGES_PATH / filename, "rb") as f:
        _ext = filename.split(".")[-1]
        _key = filename.replace(".", "_")
        attachment = MIMEImage(f.read(), _subtype=_ext)
        attachment.add_header("Content-ID", _key)
        attachment.add_header('Content-Disposition', f"attachment; filename= {filename}")
        attachments_dict[_key] = attachment
