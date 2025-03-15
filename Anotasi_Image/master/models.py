from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

class CustomUserManager(BaseUserManager):
    """Custom manager untuk model CustomUser agar mendukung login dengan email atau username."""

    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email harus diisi!")
        email = self.normalize_email(email)
        extra_fields.setdefault("is_active", False)  # Default akun belum aktif
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)  # Superuser langsung aktif
        return self.create_user(username, email, password, **extra_fields)

class CustomUser(AbstractUser):
    """Model user kustom dengan tambahan email sebagai field unik dan nomor HP."""
    
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    phone_number = models.CharField(max_length=15, unique=True, blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False)  # User harus aktivasi dulu via email
    
    objects = CustomUserManager()  # Manager kustom

    USERNAME_FIELD = "email"  # Login default pakai email
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email
