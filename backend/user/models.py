from django.db import models
from django.utils import timezone
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)


class CustomAccountManager(BaseUserManager):
    def create_superuser(
        self, email, username, first_name, last_name, password, **other_fields
    ):
        other_fields.setdefault("is_staff", True)
        other_fields.setdefault("is_superuser", True)
        other_fields.setdefault("is_active", True)

        if other_fields.get("is_staff") is not True:
            raise ValueError("Superuser must be assigned to is_staff=True")
        if other_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must be assigned to is_superuse=True")

        return self.create_user(
            email, username, first_name, last_name, password, **other_fields
        )

    def create_user(
        self, email, username, first_name, last_name, password, **other_fields
    ):
        if not email:
            raise ValueError("You must provide an email address")

        email = self.normalize_email(email)
        user = self.model(
            email=email,
            username=username,
            first_name=first_name,
            last_name=last_name,
            **other_fields
        )
        user.set_password(password)
        user.save()
        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField("Email Address", unique=True)
    username = models.CharField(max_length=30, unique=True)
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    join_date = models.DateTimeField(default=timezone.now)
    about = models.TextField("About", max_length=500, blank=True)
    is_staff = models.BooleanField(default=False)
    # TODO default to false and require email verification
    is_active = models.BooleanField(default=True)

    objects = CustomAccountManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    def __str__(self):
        return self.username
