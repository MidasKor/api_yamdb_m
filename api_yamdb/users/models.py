"""User's custom model"""
from django.db import models
from django.contrib.auth.models import AbstractUser

from .manager import UserManager

USER = 'user'
MODERATOR = 'moderator'
ADMIN = 'admin'

ROLES = [
    (USER, USER),
    (MODERATOR, MODERATOR),
    (ADMIN, ADMIN),
]


class User(AbstractUser):
    """User's custom model."""
    username = models.CharField(
        "username",
        max_length=150,
        unique=True,
        blank=False,
        help_text="Required. 150 characters or fewer."
    )

    email = models.EmailField(
        verbose_name="почтовый адрес",
        unique=True,
        blank=False)

    first_name = models.CharField(
        verbose_name="Имя",
        max_length=150,
        blank=True)

    last_name = models.CharField(
        verbose_name="Фамилия",
        max_length=150,
        blank=True)

    bio = models.TextField(verbose_name="Биография", blank=True)

    role = models.CharField(
        verbose_name="Роль",
        max_length=15,
        choices=ROLES,
        default=USER
    )
    confirmation_code = models.CharField(
        verbose_name="Код подтверждения",
        blank=True,
        max_length=50
    )
    token = models.CharField(max_length=36, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def save(self, *args, **kwargs):
        super(User, self).save(*args, **kwargs)
        return self

    def __str__(self):
        return self.email

    @property
    def is_moderator(self):
        return self.role == MODERATOR

    @property
    def is_admin(self):
        return self.role == ADMIN

    class Meta:
        verbose_name = "Пользователь"

    def __str__(self):
        return self.username
