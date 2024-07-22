from django.core.management.base import BaseCommand, CommandError

from contrib.users.models import User
from rest_framework.authtoken.models import Token

superuser_data = dict(
    username="reho24",
    email="reho@test.com",
    is_staff=True,
    is_superuser=True,
)


class Command(
    BaseCommand
):
    def add_arguments(self, parser):
        pass

    def handle(self, *args, **kwargs):
        self.create_default_superuser()

    @staticmethod
    def create_default_superuser():
        if not (user := User.objects.filter(username=superuser_data["username"]).first()):
            print("Creating superuser.")
            user = User(**superuser_data)
            user.set_password("Reho24@$")
            user.save()
            Token.objects.get_or_create(user=user)
        return user
