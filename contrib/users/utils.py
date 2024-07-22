from contrib.utils.date_time import get_timestamp
from .models import User


class GuestUser:
    def __init__(self):
        self._username = f"user_{get_timestamp()}"

    @property
    def username(self) -> str:
        return self._username

    @property
    def email(self) -> str:
        return f"{self.username}@example.com"

    @property
    def is_verified(self) -> bool:
        return False

    @property
    def user(self):
        return User(
            username=self.username,
            email=self.email,
            is_verified=self.is_verified,
        )
