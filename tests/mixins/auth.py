from rest_framework.authtoken.models import Token

from api.auth.otp import OtpManager
from contrib.common.redis import redis_client
from contrib.users.models import User
from .client import Client


class AuthSetupMixin:
    @classmethod
    def setup_auth_data(cls):
        cls.email = "radimir.shevchenko@gmail.com"
        cls.client = Client()
        cls.obtain()
        cls.verify()
        cls.set_auth()

    @classmethod
    def obtain(cls):
        res = cls.client.post("/api/v1/auth/otp/email/obtain", data={"email": cls.email})
        assert res.json()["success"]
        cls.code = OtpManager("email", cls.email).get_code()

    @classmethod
    def verify(cls):
        res = cls.client.post("/api/v1/auth/otp/email/verify", data={"email": cls.email, "code": cls.code})
        cls.token = res.json()["token"]

    @staticmethod
    def get_auth_header(token):
        return {"Authorization": f"Bearer {token}"}

    @classmethod
    def set_auth(cls):
        cls.user = User.objects.get(email=cls.email)
        cls.user.is_staff = cls.user.is_superuser = True
        cls.user.save()
        cls.token = Token.objects.get(key=cls.token)
        cls.auth_header = cls.get_auth_header(cls.token.key)
