from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

class CustomUserManager(BaseUserManager):
    """Custom manager untuk model CustomUser agar mendukung login dengan email atau username."""

    def get_by_natural_key(self, username):
        # Try to fetch by email first
        try:
            return self.get(email=username)
        except self.model.DoesNotExist:
            # If not found, try username
            return self.get(username=username)
        
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email harus diisi!")
        email = self.normalize_email(email)
        extra_fields.setdefault("is_active", True)
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
    
    ROLE_CHOICES = [
        ('guest', 'Guest'),
        ('annotator', 'Annotator'),
        ('reviewer', 'Reviewer'),
        ('member', 'Member'),
    ]
    
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    phone_number = models.CharField(max_length=15, unique=True, blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)  # Changed to True
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='guest')
    
    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]
    
    def save(self, *args, **kwargs):
        # Ensure the user is active when saved
        self.is_active = True
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email
    
