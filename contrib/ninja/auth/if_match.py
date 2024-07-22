import jwt

from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from ninja.security import HttpBearer
from ninja.errors import HttpError

from ..schemas import UserInfo


class AuthIfMatch(HttpBearer):
    openapi_scheme = "token"
    header = "If-Match"
    is_async = True

    def __init__(self, audience: str | list[str]):
        self.audience = audience

    def decode(self, token):
        try:
            return jwt.decode(token, settings.SECRET_KEY, audience=self.audience, algorithms=["HS256"])
        except: ...

    async def authenticate(self, request, token):
        _data = self.decode(token)
        if not _data:
            return False
        User = get_user_model()
        _user = await User.objects.filter(pk=_data["user_id"]).afirst()
        request.user = _user
        request.data = _data
        return True
