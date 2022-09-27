from django.contrib.auth.models import AbstractUser
from django.db import models

MODERATOR = 'moderator'
ADMIN = 'admin'


class User(AbstractUser):
    USER = 'user'

    roles = (
        (USER, USER),
        (MODERATOR, MODERATOR),
        (ADMIN, ADMIN),
    )

    username = models.CharField(
        max_length=150,
        unique=True
    )
    email = models.EmailField(
        max_length=249,
        unique=True
    )
    first_name = models.CharField(
        max_length=150,
        default="",
        blank=True
    )
    last_name = models.CharField(
        max_length=150,
        default="",
        blank=True
    )
    bio = models.TextField(
        default="",
        blank=True
    )
    role = models.CharField(
        max_length=16,
        default=USER,
        choices=roles
    )

    @property
    def is_admin(self):
        return self.role == ADMIN or self.is_superuser or self.is_staff

    @property
    def is_moderator(self):
        return self.role == MODERATOR
