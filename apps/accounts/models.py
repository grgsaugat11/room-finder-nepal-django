import random
from datetime import timedelta

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(
        self,
        email,
        first_name="",
        last_name="",
        phone="",
        password=None,
        **extra_fields
    ):
        if not email:
            raise ValueError("The Email field is required")

        email = self.normalize_email(email)

        user = self.model(
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            **extra_fields
        )

        if not user.username:
            user.username = email

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self,
        email,
        first_name="",
        last_name="",
        phone="",
        password=None,
        **extra_fields
    ):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("role", "admin")
        extra_fields.setdefault("email_verified", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            password=password,
            **extra_fields
        )


class User(AbstractUser):
    ROLE_TENANT = 'tenant'
    ROLE_LANDLORD = 'landlord'
    ROLE_ADMIN = 'admin'

    ROLE_CHOICES = [
        (ROLE_TENANT, 'Tenant'),
        (ROLE_LANDLORD, 'Landlord'),
        (ROLE_ADMIN, 'Admin'),
    ]

    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, unique=True)

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=ROLE_TENANT
    )

    email_verified = models.BooleanField(default=False)

    username = models.CharField(
        max_length=150,
        unique=True,
        blank=True,
        null=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'phone']

    objects = UserManager()

    def __str__(self):
        full_name = self.get_full_name()
        if full_name:
            return f"{full_name} ({self.email})"
        return self.email

    @property
    def is_tenant(self):
        return self.role == self.ROLE_TENANT

    @property
    def is_landlord(self):
        return self.role == self.ROLE_LANDLORD

    @property
    def is_platform_admin(self):
        return self.role == self.ROLE_ADMIN


class EmailOTP(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='email_otp'
    )

    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=5)

    @staticmethod
    def generate_otp():
        return str(random.randint(100000, 999999))

    def __str__(self):
        return f"OTP for {self.user.email}"