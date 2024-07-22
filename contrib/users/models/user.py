"""
Custom User model and manager
"""
from uuid import uuid4

from rest_framework.authtoken.models import Token

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from contrib.common.models import UuidTsModel
from contrib.utils.text import phone_str

from .unused import UnusedGuesAccountsMixin


class CustomBaseUserManager(UnusedGuesAccountsMixin, BaseUserManager):
    """
    Custom user model manager where phone is the unique identifiers
    for authentication instead of usernames.
    """
    def create_user(self, **extra_fields):
        """
        Create and save a User with the given phone and set passwordless.
        """
        user: BaseUserManager = self.model(**extra_fields)
        user.set_unusable_password()
        user.save()
        return user

    def create_superuser(self, username, password, **extra_fields):
        """
        Create and save a SuperUser with the given phone and password.
        """

        if password is None:
            raise TypeError('Superusers must have a password.')

        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.is_superuser = True
        user.is_staff = True
        user.save()
        Token.objects.get_or_create(user=user)
        return user


class User(AbstractBaseUser, PermissionsMixin, UuidTsModel):
    """
    User model
    """
    username = models.CharField(unique=True, max_length=70, blank=True, null=True)
    # email = models.EmailField('email', unique=True, null=True, blank=True)
    # phone = models.CharField(unique=True, max_length=70, blank=True, null=True)
    email = models.EmailField('email', null=True, blank=True)
    phone = models.JSONField(unique=True, blank=True, null=True)
    contact_phone = models.JSONField(blank=True, null=True)
    last_name = models.CharField('Фамилия', max_length=70, blank=True, null=True)
    first_name = models.CharField('Имя', max_length=70, blank=True, null=True)
    middle_name = models.CharField('Отчество', max_length=70, blank=True, null=True)
    birth_date = models.DateField(null=True, blank=True)

    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField('active', default=True)
    is_verified = models.BooleanField(default=True)

    avatar = models.ImageField(upload_to="avatars", null=True, blank=True)

    USERNAME_FIELD = 'username'
    #REQUIRED_FIELDS = ['email',]

    objects = CustomBaseUserManager()

    @property
    def token(self):
        try:
            return self.auth_token
        except:
            Token.objects.get_or_create(user=self)
        return self.auth_token

    @property
    def fio(self):
        return " ".join((x for x in (self.last_name, self.first_name, self.middle_name) if x))

    @property
    def phone_str(self):
        return phone_str(self.phone)

    def __str__(self):
        """
        Object name
        """
        return f"{self.username} ({self.email})"

    class Meta:
        """
        It's persisted model
        """
        verbose_name = 'user'
        verbose_name_plural = 'users'
