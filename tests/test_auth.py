from django.test import TestCase

from api.auth.otp import OtpManager
from .mixins import AuthSetupMixin


class AuthTestCase(AuthSetupMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.setup_auth_data()

    def test_user(self):
        assert self.user.is_active

    def test_skip(self):
        res = self.client.post(f"/api/v1/auth/skip")
        token = res.json()["token"]
        auth_header = self.get_auth_header(token)
        res = self.client.get(f"/api/v1/profile", headers=auth_header)
        assert res.json()["is_verified"] == False

    def test_change_email(self):
        _email = f"new_{self.email}"
        _data = {"email": _email}
        # Send code
        res = self.client.post(f"/api/v1/auth/otp/email/obtain", data=_data,
            content_type="application/json")
        assert res.json()["success"]
        _code = OtpManager("email", _email).get_code()
        # Change email
        res = self.client.post(f"/api/v1/auth/email/change", data={**_data, "code": _code},
            headers=self.auth_header, content_type="application/json")
        assert res.json()["email"] == _email
